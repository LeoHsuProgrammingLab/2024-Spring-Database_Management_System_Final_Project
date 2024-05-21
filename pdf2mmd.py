# nougat <file_name> --out <output_dir> --no-skipping

import subprocess
import pandas as pd
import requests
from download_and_getRef import *
from tqdm.auto import tqdm

def download_file(url, save_path):
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
    arxiv_list = [id[-10:] for id in papers['Arxiv Link'].values]

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
