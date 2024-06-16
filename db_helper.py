import dotenv, os
import importlib.util
import subprocess
import sys
from neo4j import GraphDatabase
import re
import ast
from tex_helper import *
import numpy as np
import time
from utils import *
from semantic_search.embed_extractor import LLM

package_spec = importlib.util.find_spec('alive_progress')
if package_spec is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'alive_progress'])

from alive_progress import alive_bar 

from google.api_core.exceptions import ResourceExhausted

class Neo4j_interface:
    def __init__(self, conn_info='credential.txt'):
        load_status = dotenv.load_dotenv(conn_info)
        if load_status is False:
            raise RuntimeError('Environment variables not loaded.')

        URI = os.getenv("NEO4J_URI")
        AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
        self.driver = GraphDatabase.driver(URI, auth=AUTH)
        self.driver.verify_connectivity()
        self.llm = LLM()    

    def __del__(self):
        self.close()

    def close(self):
        self.driver.close()

    def exec_query(self, query, printout=True):
        records, summary, keys = self.driver.execute_query(query, database_="neo4j")
        return records

    def get_author_topics(self, author, f=2):
        records = self.exec_query(f"""
            MATCH (:Author {{name: '{author}'}})-[:publishes]->(d:Title)-[:has_topic]->(k:Keyword)
            RETURN collect(k.content) AS keyword_list
        """)
        
        frequency = dict()
        for key in records[0]['keyword_list']:
            if key in frequency:
                frequency[key] += 1
            else:
                frequency[key] = 1
        
        topics = [key for key in frequency if frequency[key] >= f]
        if len(topics) == 0:
            return topics

        for topic in topics:
            query = f"""
                MATCH (a:Author {{name: '{author}'}}), (k:Keyword {{content: '{topic}'}})
                MERGE (a)-[s:studies]->(k)
                SET s.degree={f}
                MERGE (k)-[e:has_expert]->(a)
                SET e.degree={f}
            """
        self.exec_query(query)

        return topics

    def get_same_area_authors(self, author):
        records = self.exec_query(f"""
            MATCH (:Author {{name: '{author}'}})-[:studies]->(:Keyword)-[:has_expert]->(a:Author)
            WHERE a.name <> '{author}'
            RETURN a.name as name
        """)
        authors = [record['name'] for record in records]
        return authors
    
    def get_author_num(self):
        number = self.exec_query('MATCH (n:Author) RETURN count(n)')[0]['count(n)']
        print("number of authors: ", number)
        return number
    
    def get_title_num(self):
        number = self.exec_query('MATCH (n:Title) RETURN count(n)')[0]['count(n)']
        print("number of titles: ", number)
        return number
    
    def get_all_nodes_num(self):
        number = self.exec_query('MATCH (n) RETURN COUNT(n)')
        print("nodes: ", number)
        return number
    
    def get_all_relationships_num(self):
        number = self.exec_query('MATCH ()-[r]->() RETURN COUNT(r)')
        print("relationships: ", number)
        return number

    def get_all_outline_num(self):
        outlines = self.exec_query('MATCH (o:Outline) RETURN COUNT(o)')
        print("outlines: ", outlines)
        return outlines
    
    def get_all_embed_num(self):
        embeds = self.exec_query('MATCH (e:Embedding) RETURN COUNT(e)')
        print("embeds: ", embeds)
        return embeds
    
    def get_all_keyword_num(self):
        keywords = self.exec_query('MATCH (k:Keyword) RETURN COUNT(k)')
        print("keywords: ", keywords)
        return keywords

    def search_k_similar(self, paper_title, k=5, including_self=True):
        if including_self:
            k += 1
        # including self
        index_query = f"""
            MATCH (t:Title {{name: '{paper_title}'}})
            CALL db.index.vector.queryNodes('embedding', {k}, t.embedding) YIELD node, score
            RETURN node.name, score
        """
        records = self.exec_query(index_query)
        k_similar_papers = [(record['node.name'], record['score']) for record in records]
        return k_similar_papers

    def insert_a_paper(self, title, arxiv_id, authors, abstract, content, references, keywords, embedding):
        # Construct parameter dictionary
        params = {
            "title": title,
            "arxiv_id": arxiv_id,
            "outline": abstract,
            "content": content,
            "embedding": embedding,
            **{f"keyword_{i}": keyword for i, keyword in enumerate(keywords)},
            **{f"author_{i}": name for i, name in enumerate(authors)},
            **{f"reference_title_{i}": ref['title'] for i, ref in enumerate(references)}
            # **{f"author_ref_{i}_{j}": ref_author for i, ref in enumerate(references) for j, ref_author in enumerate(ref['authors'])}
        }

        # Initialize query parts
        merge_authors_and_link = ""
        merge_reference_and_link = ""
        merge_keywords_and_link = ""

        # Merge authors and create relationships
        for i, author in enumerate(authors):
            merge_authors_and_link += f"""
                MERGE (a_{i}:Author {{name: $author_{i}}})
                CREATE (a_{i})-[:publishes]->(t)
                CREATE (t)-[:published_by]->(a_{i})
            """
        
        # Merge references and create relationships
        for i, ref in enumerate(references):
            merge_reference_and_link += f"""
                MERGE (ref_{i}:Title {{name: $reference_title_{i}}})
                CREATE (t)-[:references]->(ref_{i})
                CREATE (ref_{i})-[:referenced_by]->(t)
            """
            # for j, ref_author in enumerate(ref['authors']):
            #     merge_reference_and_link += f"""
            #         MERGE (:Author {{name: $author_ref_{i}_{j}}})-[:publishes]->(:Title {{content: $reference_title_{i}}})
            #         MERGE (:Title {{content: $reference_title_{i}}})-[:published_by]->(:Author {{name: $author_ref_{i}_{j}}})
            #     """

        # Merge keywords and create relationships
        for i, keyword in enumerate(keywords):
            merge_keywords_and_link += f"""
                MERGE (k_{i}:Keyword {{content: $keyword_{i}}})
                CREATE (k_{i})-[:topic_of]->(t)
                CREATE (t)-[:has_topic]->(k_{i})
            """

        # Main query for inserting the paper and its components
        query = f"""
            MERGE (t:Title {{name: $title}})
            SET t.abstract = $outline,
                t.arxiv_id = $arxiv_id,
                t.content = $content,
                t.embedding = $embedding
            {merge_authors_and_link}
            {merge_reference_and_link}
            {merge_keywords_and_link}
        """

        print('start inserting a paper')
        # Execute the query
        try:
            self.driver.execute_query(query, parameters_=params, database_='neo4j')
            print("Paper inserted successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def create_vector_index(self, name='embedding'):
        self.driver.execute_query(f"""
            CREATE VECTOR INDEX {name} IF NOT EXISTS
            FOR (n: Title) 
            ON (n.embedding)
            OPTIONS {{
                indexConfig: {{
                    `vector.dimensions`: 768, 
                    `vector.similarity_function`: "COSINE"
                }}
            }}
        """, database_='neo4j')

    def get_k_similar_papers(self, text, k=5):
        target_embed = self.get_embedding(text)
        all_embeds = self.get_all_embeds()
        similarities = []

        for title, embed in all_embeds:
            if title == text or embed is None:
                continue
            similarity = self.llm.calculate_similarity_by_embedding(target_embed, embed)
            similarities.append((title, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]

    def insert_keyword_of_a_paper(self, keywords, title):
        for keyword in keywords:
            self.driver.execute_query("""
                MATCH (t:Title {name: $title})
                MERGE (k:Keyword {content: $keyword})
                CREATE (k)-[:topic_of]->(t)
                CREATE (t)-[:has_topic]->(k)
                """,
                keyword=keyword, title=title, database_='neo4j'
            )

    def insert_embed_of_a_paper(self, embedding: np.ndarray, title: str): # top vector of the paper
        self.driver.execute_query("""
            CREATE (e:Embedding {content: $embedding})
            WITH e
            MATCH (t:Title {name: $title})
            CREATE (t)-[:has_embedding]->(e)
            CREATE (e)-[:embedding_of]->(t)
            """, 
            embedding=embedding, title=title, database_='neo4j'
        )

    def get_embedding(self, text: str):
        text = truncate_text_to_bytes(text)
        return self.llm.get_embedding(text)
    
    def get_all_embeds(self):
        records = self.exec_query('MATCH (n:Title) RETURN n.embedding, n.name')
        return [(record['n.name'], record['n.embedding']) for record in records]
    
    def get_keywords(self, abstract):
        return self.llm.get_keywords(abstract)
    
    def k_means_clustering(self, title: str, k=5):
        # using GDS k-means algorithm to find the papers in the same cluster as input title
        pass

    def insert_document(self, path): # path to the .tex file, in a better defined format
        with open(path, 'r') as f:
            tex = f.read()
    
        # extract nodes
        title = extract_by_label(tex, 'title')
        abstract = extract_begin_end(tex, 'abstract')[0]
        conclusion = extract_conclusion(tex)
        authors = extract_authors(tex)
        content = extract_content(tex)
        reference = extract_reference(tex)

        merge_authors_and_link = ""
        for i in range(len(authors)):
            merge_authors_and_link += """
            MERGE (author{idx}:Author {{name: '{name}'}})
            CREATE (author{idx})-[:publishes]->(title)
            CREATE (title)-[:published_by]->(author{idx}) 
            """.format(name=authors[i], idx=i)
        
        merge_reference_and_link = ""
        for i in range(len(reference)):
            merge_reference_and_link += """
            MERGE (title{idx}:Title {{content: '{title}'}})
            MERGE (title)-[:refereces]->(title{idx})
            CREATE (title{idx})-[:referenced_by]->(title)
            """.format(title=reference[i], idx=i)

        # query
        self.driver.execute_query("""
            CREATE (title:Title {content: $title})
            CREATE (outline:Outline {content: $outline})
            CREATE (title)-[:summarized_in]->(outline)
            CREATE (content:Content {content: $content})
            CREATE (title)-[:consists_of]->(content)
            CREATE (content)-[:part_of]->(title)
            """ + merge_authors_and_link + merge_reference_and_link,
            title=title, 
            outline=abstract+conclusion, 
            content=content,
            database_='neo4j'
        )
    
    # pattern matching actually becasue text2Cypher takes money
    def text2cypher(self, text: str):
        # Full title search
        pattern1 = re.compile(r"(?:title|titled|name|named)\s+[\'\"]?(.*?)(\.|\"|\'|$)")
        pattern2 = re.compile(r"(?:paper)\s+[\'\"]?(.*?)(\.|\"|\'|$)")
        match1 = re.search(pattern1, text)
        match2 = re.search(pattern2, text)
        
        if match1:
            title = match1.group(1)
        elif match2:
            title = match2.group(1)
        else:
            title = ''
        
        if title:
            title = title.lower()
            query = f"MATCH (n: Title) WHERE toLower(n.content) CONTAINS '{title}' RETURN n"
            records = self.exec_query(query, printout=False)
            for record in records:
                record = record.data()
                title = record['n']['content']
                return title
        
        # Keywords search
        pattern3 = re.compile(r"(?:with|contain|contains|contained|include|includes|included)\s+(.*?)(\.|$)")
        match3 = re.search(pattern3, text)
        if match3:
            keywords_str = match3.group(1)
            keywords_str = keywords_str.replace('"', '')
            keywords_str = keywords_str.replace("'", "")
            keywords_str = keywords_str.lower()
            pattern = r"\b(?:(?!and)\w+)\b"
            keywords = re.findall(pattern, keywords_str)
        else:
            exclude_chars = [',', '.', '"', '\'']
            for char in exclude_chars:
                text = text.replace(char, '')
            
            text = text.lower()
            keywords = text.split()
            exclude_chars = [
                'and', 'or', 
                'on', 'in', 'with', 'to',
                'get', 'find', 'include', 'gets', 'finds', 'includes',
                'title', 'name', 'paper'
            ]                
            for char in exclude_chars:
                if char in keywords:
                    keywords.remove(char)
        
        papers = {}
        for keyword in keywords:
            query = f"MATCH (n: Title) WHERE toLower(n.content) CONTAINS '{keyword}' RETURN n.content"
            records = self.exec_query(query, printout=False)
            for record in records:
                record = record.data()
                title = record['n.content']
                if title not in papers:
                    papers[title] = 1
                else:
                    papers[title] += 1

            query = f"MATCH (n: Keyword) WHERE toLower(n.content) CONTAINS '{keyword}' RETURN n.content"
            records = self.exec_query(query, printout=False)
            for record in records:
                record = record.data()
                title = record['n.content']
                if title not in papers:
                    papers[title] = 1
                else:
                    papers[title] += 1

        papers = [key for key, _ in sorted(papers.items(), key=lambda item: item[1], reverse=True)]
        return papers
    
    def cypher2text_reference(self, text: str):
        pattern1 = re.compile(r"(?:cited by|referred by|mentioned by)\s+[\'\"]?(.*?)(\.|\"|\'|$)")
        pattern2 = re.compile(r"\s+[\'\"](.*?)(\"|\')\s+(?:cite|refer|reference|mention|cites|refers|references|mentions|cited|referred|referenced|mentioned)")
        pattern3 = re.compile(r"(?:cite|refer|reference|mention|cites|refers|references|mentions|cited|referred|referenced|mentioned)\s+[\'\"]?(.*?)(\.|\"|\'|$)")
        match1 = re.search(pattern1, text)
        match2 = re.search(pattern2, text)
        match3 = re.search(pattern3, text)
        if match1:
            # print("Match1: ", match1.group(1))
            title = match1.group(1).lower()
            records = self.exec_query(f"""MATCH (n: Title)-[r: referenced_by]->(m: Title)
                                          WHERE toLower(m.content) = '{title}'
                                          RETURN n.content""", printout=False)
        elif match2:
            # print("Match2: ", match2.group(1))
            title = match2.group(1).lower()
            records = self.exec_query(f"""MATCH (n: Title)-[r: referenced_by]->(m: Title)
                                          WHERE toLower(m.content) = '{title}'
                                          RETURN n.content""", printout=False)
        elif match3:
            # print("Match3: ", match3.group(1))
            title = match3.group(1).lower()
            records = self.exec_query(f"""MATCH (m: Title)-[r: referenced_by]->(n: Title)
                                          WHERE toLower(m.content) = '{title}'
                                          RETURN n.content""", printout=False)
        else:
            records = []
        
        papers = []
        for record in records:
            data = record.data()
            papers.append(data['n.content'])

        return papers
    
    def cypher2text_author(self, text: str):
        pattern1 = re.compile(r"(?:written by|published by)\s+[\'\"]?(.*?)(\.|\"|\'|$)")
        pattern2 = re.compile(r"(?:papers that|papers from) [\'\"]?(.*?)[\'\"]?\s*(?:papers|writes|wrote|$)")
        pattern3 = re.compile(r"(?:find|get)?\s*[\'\"]?(.*?)[\'\"]?\s*(?:papers|paper)", re.IGNORECASE)
        match1 = re.search(pattern1, text)
        match2 = re.search(pattern2, text)
        match3 = re.search(pattern3, text)
        if match1:
            author = match1.group(1).lower()
            records = self.exec_query(f"""MATCH (n: Author)-[r: publishes]->(m: Title) 
                                          WHERE toLower(n.name) = \'{author}\' 
                                          RETURN m.content""", printout=False)
        elif match2:
            author = match2.group(1).lower()
            records = self.exec_query(f"""MATCH (n: Author)-[r: publishes]->(m: Title) 
                                          WHERE toLower(n.name) = \'{author}\' 
                                          RETURN m.content""", printout=False)
        elif match3:
            author = match3.group(1).lower()
            author = author.replace("'s", '')

            records = self.exec_query(f"""MATCH (n: Author)-[r: publishes]->(m: Title) 
                                          WHERE toLower(n.name) = \'{author}\' 
                                          RETURN m.content""", printout=False)
        else:
            author = text.lower()
            records = self.exec_query(f"""MATCH (n: Author)-[r: publishes]->(m: Title) 
                                          WHERE toLower(n.name) = \'{author}\' 
                                          RETURN m.content""", printout=False)
        
        papers = []
        for record in records:
            data = record.data()
            papers.append(data['m.content'])

        return papers
    
    # Find synonyms by categorizing directly
    def find_synonyms_v1(self):
        result = self.exec_query('Match (n: Keyword) return n.content', printout=False)
        keywords = [record['n.content'] for record in result]

        text  = f"Find the synonym groups in {keywords}. " +\
                "The meanings of the keywords in each group should be actually the same rather than just related or similar." +\
                "Each group should contain at most 8 keywords." +\
                "Please output with numbering list."
        response = self.llm.generate_content(text)

        # Parse the following response
        try:
            lines = response.text.strip().split('\n')
            lists = [ast.literal_eval(line.split('. ')[1]) for line in lines]
        except ValueError:
            print(f"Error in response {response}.")
            lists = []

        return lists
    
    # Find synonyms by comparing each pair of keywords
    def find_synonyms_v2(self):
        records = self.exec_query('Match (n: Keyword) return n.content', printout=False)
        keywords = [record['n.content'] for record in records]     
    
        synonyms = []
        error_pairs = []
        print(f"Comparing {len(keywords)} keywords.")
        for i in range(len(keywords)):
            with alive_bar(len(keywords)) as bar:
                j = i
                while j < len(keywords):
                    if keywords[i] == keywords[j]:
                        j += 1
                        bar()
                        continue

                    print(f"> Keyword 02: {keywords[j]}")
                    prompt = f"Are {keywords[i]} and {keywords[j]} synonyms? Only respond with 'yes' or 'no'."

                    try:
                        response = self.llm.generate_content(prompt)
                        if 'yes' in response.text.lower():
                            synonyms.append((keywords[i], keywords[j]))
                    except ResourceExhausted:
                        print("Resources are exhausted.")
                        time.sleep(30)
                        j -= 1
                    except ValueError:
                        print(f"Error in response {response}.")
                        time.sleep(5)
                        error_pairs.append((keywords[i], keywords[j]))
                    finally:
                        j += 1
                        bar()
        
        return synonyms, error_pairs

    def find_subtopic(self):
        records = self.exec_query(f"MATCH (n: Title)-[r: summarized_in]->(m: Outline) RETURN n.content, m.content", printout=False)
        keywords = []
        outlines = []
        for i in range(len(records)):
            title = records[i]['n.content']
            outline = records[i]['m.content']
            keyword_records = self.exec_query(f"MATCH (n: Title)-[r: has_topic]->(m: Keyword) WHERE n.content = '{title}' RETURN m.content", printout=False)
            
            keyword_records = [keyword['m.content'] for keyword in keyword_records]
            for keyword in keyword_records:
                keywords.append(keyword)
                outlines.append(outline)

        subtopics = {}
        error_pairs = ""
        for i, keyword1 in enumerate(keywords):
            with alive_bar(len(keywords)) as bar:
                j = 0
                while j < len(keywords):
                    keyword2 = keywords[j]
                    if keyword1 == keyword2:
                        j += 1
                        bar()
                        continue
                    
                    prompt = f"""
                        Below are two keywords and the outlines they appear. Does the latter keyword the subtopic of the former keyword?
                        Please respond with 'yes' or 'no'.

                        Keyword 1: {keyword1}
                        Outline 1: {outlines[i]}

                        Keyword 2: {keyword2}
                        Outline 2: {outlines[j]}
                    """
                    try:
                        response = self.llm.generate_content(prompt)
                        if 'yes' in response.text.lower():
                            if keyword1 not in subtopics:
                                subtopics[keyword1] = []
                            subtopics[keyword1].append(keyword2)
                    except ResourceExhausted:
                        print("Resources are exhausted.")
                        time.sleep(30)
                        j -= 1
                    except ValueError:
                        print(f"Error in response {response}.")
                        time.sleep(10)
                        error_pairs += prompt
                    finally:
                        j += 1
                        bar()

        return subtopics, error_pairs

if __name__ == '__main__':
    interface = Neo4j_interface()
    # interface.exec_query('MATCH (n) DETACH DELETE n')
    # interface.insert_document('paper/AceKG.tex')
    # interface.exec_query('MATCH (n: Author)-[r: publishes]->(m: Title) WHERE n.name = \'Fanjin Zhang\' RETURN m')
    # result = interface.exec_query('Match (n: Keyword) return n.content', printout=False)
    # keywords = [record['n.content'] for record in result]

    # records = interface.exec_query('MATCH (n:Author) RETURN n.name as name')
    # for record in records:
    #     interface.get_author_topics(record['name'])
    interface.get_same_area_authors('Ramin Ghorbani')
    # print(topics)
    # result, _ = interface.find_subtopic()
    # print(result)


            