import os
import shutil
import pandas as pd

def remove_dirs(directories: list):
    # Loop through the list of directories
    for dir in directories:
        if os.path.isdir(dir):
            print(f"Removing directory: {dir}")
            shutil.rmtree(dir)
        else:
            print(f"Directory does not exist: {dir}")

    print("Directory cleanup complete.")

if __name__ == '__main__':
    papers = pd.read_csv('./papers.csv')
    arxiv_list = [f'./{id[-10:]}' for id in papers['Arxiv Link'].values]

    remove_dirs(arxiv_list)