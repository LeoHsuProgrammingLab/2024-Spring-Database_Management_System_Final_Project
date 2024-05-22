import pandas as pd
from download_and_getRef import *
from db_helper import *
import os
import glob
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

def combine_tex_files(arxiv_id: str):
    directory = f"./paper/{arxiv_id}"
    # Change the current working directory to the specified path
    if os.path.exists(directory):
        # Change the current working directory to the specified path
        os.chdir(directory)
        # Find all .tex files in the directory
        tex_files = glob.glob('**/*.tex', recursive=True)

        # Combined content of all tex files
        combined_content = ""

        # Read each file and append its content to the combined_content string
        for filename in tex_files:
            with open(filename, 'r') as file:
                content = file.read()
                combined_content += content + "\n\n"  # Adding some space between contents of each file


        # Check if you have write permissions
        if not os.access(filename, os.W_OK):
            # Try to change the permissions
            try:
                os.chmod(filename, 0o644)
            except PermissionError:
                print(f"Cannot set write permissions for {filename}. You might need to run the script as a superuser.")
        else:
            # Write the combined content into a new file named 'paper.tex'
            with open(f'{arxiv_id}.tex', 'w') as file:
                file.write(combined_content)

        print(f"All .tex files have been combined into paper.tex in the directory {directory}")
        os.chdir("../..")
    else:
        print(f"Directory {directory} does not exist.")

def main():
    papers = pd.read_csv('./paper/papers.csv')
    arxiv_list = [id[-10:] for id in papers['Arxiv Link'].values]
    
    # Download papers from arxiv
    # for arxiv_id in arxiv_list:
    #     downlaod_papers(arxiv_id)
    
    # Combine .tex files
    # for arxiv_id in arxiv_list:
    #     combine_tex_files(arxiv_id)

    # Insert papers into database
    interface = Neo4j_interface()
    for arxiv_id in arxiv_list:
        if os.path.exists(f"./paper/{arxiv_id}/{arxiv_id}.tex"):
            interface.insert_document(f"./paper/{arxiv_id}/{arxiv_id}.tex")
            print("inserted paper: ", arxiv_id)
        else:
            print("paper .tex not found: ", arxiv_id)

if __name__ == '__main__':
    main()