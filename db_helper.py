import dotenv, os
from neo4j import GraphDatabase
import re

from tex_helper import *

class Neo4j_interface:
    def __init__(self, conn_info='credential.txt'):
        load_status = dotenv.load_dotenv(conn_info)
        if load_status is False:
            raise RuntimeError('Environment variables not loaded.')

        URI = os.getenv("NEO4J_URI")
        AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
        self.driver = GraphDatabase.driver(URI, auth=AUTH)
        self.driver.verify_connectivity()

    def __del__(self):
        self.close()

    def close(self):
        self.driver.close()

    def exec_query(self, query):
        records, summary, keys = self.driver.execute_query(query, database_="neo4j")
        print("records: ", records)
        # print("summary: ", summary)
        # print("keys: ", keys)
        return records
    
    def get_author_number(self):
        number = self.exec_query('MATCH (n:Author) RETURN count(n)')[0]['count(n)']
        print("number of authors: ", number)
        return number
    
    def get_title_number(self):
        number = self.exec_query('MATCH (n:Title) RETURN count(n)')[0]['count(n)']
        print("number of titles: ", number)
        return number
    
    def get_all_nodes(self):
        nodes = self.exec_query('MATCH (n) RETURN COUNT(n)')
        print("nodes: ", nodes)
        return nodes
    
    def get_all_relationships(self):
        relationships = self.exec_query('MATCH ()-[r]->() RETURN COUNT(r)')
        print("relationships: ", relationships)
        return relationships

    def insert_a_paper(self, title, authors, abstract, content, references):
        # Construct parameter dictionary
        params = {
            "title": title,
            "outline": abstract,
            "content": content,
            **{f"author_{i}": name for i, name in enumerate(authors)},
            **{f"reference_title_{i}": ref['title'] for i, ref in enumerate(references)}
            # **{f"author_ref_{i}_{j}": ref_author for i, ref in enumerate(references) for j, ref_author in enumerate(ref['authors'])}
        }

        # Initialize query parts
        merge_authors_and_link = ""
        merge_reference_and_link = ""

        # Merge authors and create relationships
        for i, author in enumerate(authors):
            merge_authors_and_link += f"""
                MERGE (:Author {{name: $author_{i}}})-[:publishes]->(:Title {{content: $title}})
                MERGE (:Title {{content: $title}})-[:published_by]->(:Author {{name: $author_{i}}})
            """
        
        # Merge references and create relationships
        for i, ref in enumerate(references):
            merge_reference_and_link += f"""
                MERGE (:Title {{content: $reference_title_{i}}})<-[:references]-(:Title {{content: $title}})
                MERGE (:Title {{content: $reference_title_{i}}})-[:referenced_by]->(:Title {{content: $title}})
            """
            # for j, ref_author in enumerate(ref['authors']):
            #     merge_reference_and_link += f"""
            #         MERGE (:Author {{name: $author_ref_{i}_{j}}})-[:publishes]->(:Title {{content: $reference_title_{i}}})
            #         MERGE (:Title {{content: $reference_title_{i}}})-[:published_by]->(:Author {{name: $author_ref_{i}_{j}}})
            #     """

        # Main query for inserting the paper and its components
        query = f"""
            CREATE (t:Title {{content: $title}})
            CREATE (o:Outline {{content: $outline}})
            CREATE (t)-[:summarized_in]->(o)
            CREATE (c:Content {{content: $content}})
            CREATE (t)-[:consists_of]->(c)
            CREATE (c)-[:part_of]->(t)
            {merge_authors_and_link}
            {merge_reference_and_link}
        """

        print('start inserting a paper')
        # Execute the query
        try:
            self.driver.execute_query(query, parameters_=params, database_='neo4j')
            print("Paper inserted successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def insert_document(self, path):
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
            CREATE (title)-[:refereces]->(title{idx})
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
    
    def text2cypher(self, text: str):
        if 'title' in text and 'contain' not in text:
            # 限制只能是 ... title <title>
            title = text.split('title ')[1]
            title = title.replace('"', '')
            title = title.replace("'", "")
            title = title.replace(".", "")
            query = f"MATCH (n: Title) WHERE TOLOWER(n.content) = TOLOWER('{title}') RETURN n"
            result = self.exec_query(query)
        elif 'contain' in text and 'keyword' not in text:
            keywords = text.split('contain ')[1]
            keywords = keywords.replace('"', '')
            keywords = keywords.replace("'", "")
            keywords = keywords.replace(".", "")
            keywords = keywords.split(', ')
            
            result = []
            for keyword in keywords:
                query = f"MATCH (n: Title) WHERE TOLOWER(n.content) CONTAINS TOLOWER('{keyword}') RETURN n"
                result += self.exec_query(query)
        elif 'keyword' in text:
            pass

if __name__ == '__main__':
    interface = Neo4j_interface()
    # interface.exec_query('MATCH (n) DETACH DELETE n')
    # interface.insert_document('paper/AceKG.tex')
    interface.exec_query('MATCH (n) RETURN n')
    # interface.exec_query(f"MATCH (n: Title) WHERE n.content = 'Regular Path Query Evaluation on Streaming Graphs' RETURN n")

    text1 = "Find papers with title 'Regular Path Query Evaluation on Streaming Graphs'."
    text2 = "Get papers with title Regular Path Query Evaluation on Streaming Graphs."
    text3 = "Find papers that the title contain 'Query', 'Graph'."
    # interface.text2cypher(text3)