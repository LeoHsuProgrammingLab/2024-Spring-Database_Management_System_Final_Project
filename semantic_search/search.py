import sys
sys.path.append('..')
from db_helper import Neo4j_interface

if __name__ == "__main__":
    interface = Neo4j_interface(conn_info='../credential.txt')
    title = 'Convolutional LSTM Network: A Machine Learning Approach for Precipitation Nowcasting'
    # result = interface.exec_query('DROP INDEX embedding')
    # result = interface.exec_query('SHOW VECTOR INDEXES')
    # interface.create_vector_index()
    result = interface.search_k_similar(title, k=5)
    print(result)