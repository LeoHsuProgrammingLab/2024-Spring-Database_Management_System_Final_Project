import pandas as pd
from download_and_getRef import *
from db_helper import *
import os
import shutil

def downlaod_papers(arxiv_id: str): # download papers from arxiv for .zip & .pdf
    url = f"https://arxiv.org/src/{arxiv_id}"
    url2= f"https://arxiv.org/pdf/{arxiv_id}"
    save_dir = f"./paper/{arxiv_id}"
    tar_gz_path = f"./paper/{arxiv_id}.tar.gz"
    pdf_path = f"./paper/{arxiv_id}/{arxiv_id}.pdf"

    if not os.path.exists(save_dir):
        download_file(url, tar_gz_path)
        try:
            unzip_tar_gz(tar_gz_path, save_dir)
            download_file(url2, pdf_path)
            remove_file(tar_gz_path)
        except:
            print("unzip error: ", arxiv_id)
            remove_file(tar_gz_path)

def main():
    papers = pd.read_csv('./paper/papers.csv')
    arxiv_list = [id[-10:] for id in papers['Arxiv Link'].values]
    
    interface = Neo4j_interface()
    for arxiv_id in arxiv_list:
        downlaod_papers(arxiv_id)
        
        if os.path.exists(f"./paper/{arxiv_id}/{arxiv_id}.tex"):
            interface.insert_document(f"./paper/{arxiv_id}/{arxiv_id}.tex")
            print("inserted paper: ", arxiv_id)
        else:
            print("paper .tex not found: ", arxiv_id)

if __name__ == '__main__':
    main()