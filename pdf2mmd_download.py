# nougat <file_name> --out <output_dir> --no-skipping

import subprocess
import pandas as pd
import requests
import glob
from download_and_getRef import *
from tqdm.auto import tqdm

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

def downlaod_papers_tex(arxiv_id: str): # download papers from arxiv for .zip & .pdf
    print("downloading paper: ", arxiv_id)
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

def download_mmd(url, save_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True  # Return True when download is successful
    except requests.RequestException as e:
        print(f"Failed to download file from {url}. Error: {e}")
        return False  # Return False if download fails

def main():
    papers = pd.read_csv('./paper/papers.csv')
    arxiv_list = [id.split('/')[-1] for id in papers['Arxiv Link'].values]

    for arxiv_id in tqdm(arxiv_list):
        if not os.path.exists(f"./papers/{arxiv_id}"):
            os.makedirs(f"./papers/{arxiv_id}")

        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        save_path = f"./papers/{arxiv_id}/{arxiv_id}.pdf"

        # downlaod_papers_tex(arxiv_id)
        
        if download_file(pdf_url, save_path):
            command = f"nougat {save_path} --out ./papers/{arxiv_id} --no-skipping"
            result = subprocess.run(command, capture_output=True, text=True, shell=True)  # Added shell=True for command string
            
            # Check if the command was successful
            if result.returncode == 0:
                print("Command executed successfully for:", save_path)
            else:
                print("Error running command for:", save_path)
                print("Error output:", result.stderr)
        else:
            print(f"Skipping command execution due to failed download: {arxiv_id}")
    
if __name__ == "__main__":
    main()
