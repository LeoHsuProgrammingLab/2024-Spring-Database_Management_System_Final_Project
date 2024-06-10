# nougat <file_name> --out <output_dir> --no-skipping

import subprocess
import pandas as pd
import requests
import glob
from download_and_getRef import *
from getID import *
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
                try:
                    content = file.read()
                    combined_content += content + "\n\n"  # Adding some space between contents of each file
                except UnicodeDecodeError:
                    print(f"Cannot read {filename}. It might be a binary file.")


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

def unzip_paper_tex(arxiv_id: str): # download papers from arxiv for .zip & .pdf
    # pdf_url= f"https://arxiv.org/pdf/{arxiv_id}"
    save_dir = f"./paper/{arxiv_id}"
    tar_gz_path = f"./paper/{arxiv_id}.tar.gz"
    # pdf_path = f"./paper/{arxiv_id}/{arxiv_id}.pdf"

    # download_file(pdf_url, pdf_path)

    try:
        unzip_tar_gz(tar_gz_path, save_dir)
        remove_file(tar_gz_path)
    except:
        print("Failed to unzip: ", arxiv_id)
        remove_file(tar_gz_path)

def download_zip(arxiv_id: str, overwrite=True):
    url = f"https://arxiv.org/e-print/{arxiv_id}"
    tar_gz_path = f"./paper/{arxiv_id}.tar.gz"
    download_file(url, tar_gz_path, overwrite=True)

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

def preprocess_references():
    papers = pd.read_csv('./data_log/papers.csv')
    arxiv_list = [id.split('/')[-1] for id in papers['Arxiv Link'].values]

    all_other_references = []
    for arxiv_id in tqdm(arxiv_list):
        reference = extract_reference(arxiv_id)
        all_other_references += [ref['title'] for ref in reference if ref['title'] not in all_other_references]
        print(f"References found for {arxiv_id}: {len(reference)}, Total References: {len(all_other_references)}")

    with open("data_log/all_other_references.txt", "w") as f:
        for ref in all_other_references:
            f.write(ref + "\n")
    
    ref_arxiv_id_list = get_Id_by_Title_list(all_other_references)
    print(f"Total references found: {len(ref_arxiv_id_list)}")
    with open("data_log/ref_arxiv_id_list.txt", "w") as f:
        for ref_id in ref_arxiv_id_list:
            f.write(ref_id + "\n")

def main():

    with open('data_log/all_arxiv_id_list.txt', 'r') as f:
        arxiv_list = f.read().splitlines()
    print(f"Total papers found: {len(arxiv_list)}")

    # Download papers and unzip
    # for arxiv_id in tqdm(arxiv_list):
    #     download_zip(arxiv_id)
    #     unzip_paper_tex(arxiv_id)

    # Combine all .tex files into one
    for (i, arxiv_id) in enumerate(arxiv_list):
        print(f"Combining .tex files for paper {i+1}/{len(arxiv_list)}")
        combine_tex_files(arxiv_id)

    # Download papers and convert to .mmd
    for arxiv_id in tqdm(arxiv_list): 
        if not os.path.exists(f"./papers/{arxiv_id}"):
            os.makedirs(f"./papers/{arxiv_id}")

        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        save_path = f"./papers/{arxiv_id}/{arxiv_id}.pdf"
        
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
