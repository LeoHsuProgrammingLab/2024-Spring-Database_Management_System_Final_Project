import sys
sys.path.append('..')
from db_helper import Neo4j_interface

if __name__ == "__main__":
    interface = Neo4j_interface(conn_info='../credential.txt')
    text = input("Please input what you want to search: ")
    k_papers = interface.get_k_similar_papers(text, 5)
    titles = [title for title, _ in k_papers]
    scores = [score for _, score in k_papers]

    for title, score in zip(titles, scores):
        print(title, round(score, 2))