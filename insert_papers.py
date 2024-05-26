import pandas as pd
from download_and_getRef import *
from db_helper import Neo4j_interface
from mmd_helper import *
from arxiv_web_helper import *
from tqdm.auto import tqdm
import os
import glob
import shutil

interface = Neo4j_interface(conn_info='credential.txt')

def main():
    papers = pd.read_csv('./paper/papers.csv')
    arxiv_list = [id.split('/')[-1] for id in papers['Arxiv Link'].values]

    # Insert papers into database

    # interface.exec_query('MATCH (n) DETACH DELETE n')
    no_paper = 0
    for i, arxiv_id in enumerate(tqdm(arxiv_list)):
        print(arxiv_id)

        if i == 44:
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
            no_paper += 1
            print(f"{no_paper} paper not found: ", arxiv_id)
            continue

        interface.insert_a_paper(title, authors, abstract, content, reference)
        embedding = interface.get_embedding(content)
        interface.insert_embed_of_a_paper(embedding, title)
        keywords = interface.get_keywords(abstract)
        interface.insert_keyword_of_a_paper(keywords, title)

if __name__ == '__main__':
    main()
    interface.get_all_nodes()
    interface.get_all_relationships()
    interface.get_author_number()
    interface.get_title_number()
    interface.get_all_outline_num()
    interface.get_all_keyword_num()
    interface.get_all_embed_num()