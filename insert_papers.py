import pandas as pd
from download_and_getRef import *
from db_helper import Neo4j_interface
from mmd_helper import *
from arxiv_web_helper import *
from tqdm.auto import tqdm
import os

interface = Neo4j_interface(conn_info='credential.txt')

def main(reconstruct = False):
    with open("data_log/all_arxiv_id_list.txt", "r") as f:
        arxiv_list = f.read().splitlines()

    # Check if need to reconstruct the database
    if reconstruct:
        interface.exec_query('MATCH (n) DETACH DELETE n')

    # Insert papers into database
    no_paper = 0
    for i, arxiv_id in enumerate(tqdm(arxiv_list)):
        print(arxiv_id)

        if i == 117 or i < 106: # skip the paper that cannot be extracted
            continue

        title = extract_title(arxiv_id)
        authors = extract_author(arxiv_id)
        abstract = extract_abstract(arxiv_id)
        content = ""
        reference = ""
        
        if os.path.exists(f"./paper/{arxiv_id}/{arxiv_id}.tex"):
            reference = extract_reference(arxiv_id)
        else:
            print("paper .tex not found: ", arxiv_id)

        if os.path.exists(f"./papers/{arxiv_id}/{arxiv_id}.mmd"):
            with open(f"./papers/{arxiv_id}/{arxiv_id}.mmd", 'r') as f:
                mmd = f.read()
            content = extract_content(mmd)
            conclusion = extract_conclusion(mmd)
            content += conclusion

        if title == '' or authors == '' or abstract == '' or content == '' or reference == '':
            print(title == '', authors == '', abstract == '', content == '', reference == '')
            no_paper += 1
            print(f"{no_paper} paper not found: ", arxiv_id)
            continue
        
        embedding = interface.get_embedding(content)
        keywords = interface.get_keywords(abstract)
        interface.insert_a_paper(title, arxiv_id, authors, abstract, content, reference, keywords, embedding)
        interface.create_vector_index()    

if __name__ == '__main__':
    main(reconstruct=False)