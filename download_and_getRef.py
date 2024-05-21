import requests
import tarfile
import os
import re

def download_file(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as file:
        file.write(response.content)

def unzip_tar_gz(file_path, extract_path):
    with tarfile.open(file_path, "r:gz") as tar:
        tar.extractall(extract_path)

def remove_file(file_path):
    os.remove(file_path)

def find_bib_files(folder_path):
    bib_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".bib"):
                bib_files.append(os.path.join(root, file))
    return bib_files

def find_bbl_files(folder_path):
    bbl_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".bbl"):
                bbl_files.append(os.path.join(root, file))
    return bbl_files

def find_bib_refs(files):
    ref = []
    print("bib files: ",files)
    if len(files) > 0:
        for file in files:
            with open(file, 'r') as file:
                data = file.read()
            
            lines = re.split(r',\s*\n', data)
            # lines = data.splitlines()
            for line in lines:
                line = line.strip()
                if re.match(r'^title\s*=', line):
                    cleaned_line = re.sub(r'^title\s*=\s*', '', line)
                    cleaned_line = re.sub(r',$', '', cleaned_line)
                    while True:
                        cleaned_line, count1 = re.subn(r'^\{(.*)\}$', r'\1', cleaned_line)
                        cleaned_line, count2 = re.subn(r'^"(.*)"$', r'\1', cleaned_line)
                        if count1 + count2 == 0:
                            break
                    cleaned_line = cleaned_line.replace('{\\textquoteright}', '\'')
                    cleaned_line = cleaned_line.replace('{', '').replace('}', '').replace('\n', '')
                    cleaned_line = re.sub(r'\s+', ' ', cleaned_line)
                    if cleaned_line not in ref:
                        ref.append(cleaned_line)
    
    return ref

def find_bbl_refs(files):
    ref = []
    print("bbl files: ", files)
    if len(files) > 0:
        for file in files:
            with open(file, 'r') as file:
                data = file.read()

            bbl_items = re.split(r'\\bibitem', data)
            for item in bbl_items[1:]:
                newblocks = re.split(r'\\newblock', item)
                if len(newblocks) > 2:
                    bbl_content = newblocks[1].strip()
                    cleaned_line = bbl_content.replace('{', '').replace('}', '').replace('\n', '').replace('\\em', '')
                    cleaned_line = re.sub(r'.$', '', cleaned_line)
                    cleaned_line = cleaned_line.strip()
                    if cleaned_line not in ref:
                        ref.append(cleaned_line)
    
    return ref

if __name__ == "__main__":

    target=input("input the paper index: ").strip()
    # ex: https://arxiv.org/abs/2405.12117

    url = f"https://arxiv.org/src/{target}"
    url2= f"https://arxiv.org/pdf/{target}"
    tar_gz_path = f"./paper/{target}.tar.gz"
    pdf_path = f"./paper/{target}/{target}.pdf"
    save_path = f"./paper/{target}"
    ref=[]

    if not os.path.exists(save_path):    
        download_file(url, tar_gz_path)
        unzip_tar_gz(tar_gz_path, save_path)
        download_file(url2, pdf_path)
        remove_file(tar_gz_path)
        
    files1 = find_bib_files(save_path)
    files2 = find_bbl_files(save_path)
    if len(files1) > 0:
        ref = find_bib_refs(files1)
    elif len(files2) > 0:
        ref = find_bbl_refs(files2)
    print("ref count: ",len(ref))
    print("ref list: ")
    for i in ref:
        print(i)