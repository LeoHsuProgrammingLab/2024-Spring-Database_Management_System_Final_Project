import pandas as pd
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from db_helper import Neo4j_interface

def fetch_papers_and_keywords():
    query = """
    MATCH (p:Paper)-[:HAS_KEYWORD]->(k:Keyword)
    RETURN p.id AS paper_id, k.name AS keyword
    """
    
    driver = Neo4j_interface().driver   
    with driver.session() as session:
        result = session.run(query)
        data = [(record['paper_id'], record['keyword']) for record in result]
    return pd.DataFrame(data, columns=['paper_id', 'keyword'])

def sample():
    # Sample documents
    documents = [
        "the cat sat on the mat",
        "the dog sat on the log",
        "cats and dogs are great pets"
    ]

    # Initialize the TF-IDF vectorizer
    vectorizer = TfidfVectorizer()

    # Fit and transform the documents to a TF-IDF matrix
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Get feature names (terms)
    feature_names = vectorizer.get_feature_names_out()

    # Convert TF-IDF matrix to a DataFrame for better readability
    df_tfidf = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)
    print(df_tfidf)
    cosine_sim = cosine_similarity(tfidf_matrix)
    print(cosine_sim)

    with open('sample_similarity.json', 'w') as f:
        json.dump(cosine_sim.tolist(), f)

def concat_keywords(keyword_list):
    keyword_list = keyword_list.tolist()
    keyword_list = list(dict.fromkeys(keyword_list))

    for i, keyword in enumerate(keyword_list):
        # remove non-alphanumeric characters
        keyword_list[i] = re.sub(r'[^A-Za-z0-9]+', '', keyword)

    return ' '.join(keyword_list)


if __name__ == '__main__':
    # interface = Neo4j_interface()
    # records = interface.exec_query("MATCH (t:Title) -[:has_topic]-> (k:Keyword) RETURN ID(t) AS doc_id, k.content AS keyword")
    # data = [(record['doc_id'], record['keyword']) for record in records]
    # df = pd.DataFrame(data, columns=['doc_id', 'keyword'])
    # df.to_csv('basic_data.csv', sep='\t')

    df = pd.read_csv('basic_data.csv', sep='\t')

    # Combine keywords into documents
    documents = df.groupby('doc_id')['keyword'].apply(concat_keywords).reset_index()
    print(documents)
    # documents.to_csv('keywords1.csv', sep='\t')

    # documents = pd.read_csv('keywords1.csv', sep='\t')

    # Use TF-IDF to convert keywords to vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents['keyword'])
    # print(tfidf_matrix)
    # feature_names = vectorizer.get_feature_names_out()
    # print(feature_names)
    # print("Number of feature names: ", len(feature_names))

    # df_tfidf = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)
    # print(df_tfidf)

    # cosine_sim = cosine_similarity(tfidf_matrix)

    # with open('similarity.json', 'w') as f:
    #     json.dump(cosine_sim.tolist(), f)

    # print("========== cosine similarity ================")
    # print(cosine_sim)
    # print(cosine_sim.shape)