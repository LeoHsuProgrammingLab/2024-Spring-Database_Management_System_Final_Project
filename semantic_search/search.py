import sys
sys.path.append('..')
from db_helper import Neo4j_interface

if __name__ == "__main__":
    interface = Neo4j_interface(conn_info='../credential.txt')
    title = 'Convolutional LSTM Network: A Machine Learning Approach for Precipitation Nowcasting'

    # The function implemented by python cosine similarity
    result1 = interface.get_k_similar_papers(title, k=5)

    # The function implemented by Neo4j Vector Index
    # result = interface.exec_query('DROP INDEX embedding')
    # result = interface.exec_query('SHOW VECTOR INDEXES')
    # interface.create_vector_index()
    result2 = interface.search_k_similar(title, k=5)
    
    print(result1, result2, sep='\n')