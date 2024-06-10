import requests
import tarfile
import os
import re


replacements = {
    r"\'{a}": 'a', r"\'{e}": 'e', r"\'{o}": 'o', r"\'{u}": 'u', r"\'{i}": 'i', r"\'{c}": 'c', r"\'{n}": 'n', r"\'{y}": 'y',
    r"\'{A}": 'A', r"\'{E}": 'E', r"\'{O}": 'O', r"\'{U}": 'U', r"\'{I}": 'I', r"\'{N}": 'N', r"\'{Y}": 'Y',
    r"{\'a}": 'a', r"{\'e}": 'e', r"{\'o}": 'o', r"{\'u}": 'u', r"{\'i}": 'i', r"{\'c}": 'c', r"{\'n}": 'n', r"{\'y}": 'y',
    r"{\'A}": 'A', r"{\'E}": 'E', r"{\'O}": 'O', r"{\'U}": 'U', r"{\'I}": 'I', r"{\'N}": 'N', r"{\'Y}": 'Y',
    r"\={e}": 'e', r"\={E}": 'E', r"\={o}": 'o', r"\={O}": 'O', r"\={a}": 'a', r"\={A}": 'A', r"\={u}": 'u', r"\={U}": 'U', r"\={i}": 'i', r"\={I}": 'I', r"\={n}": 'n', r"\={N}": 'N', r"\={y}": 'y', r"\={Y}": 'Y',
    r"{\"{a}}": 'a', r"{\"{e}}": 'e', r"{\"{o}}": 'o', r"{\"{u}}": 'u', r"{\"{i}}": 'i', r"{\"{c}}": 'c', r"{\"{n}}": 'n', r"{\"{y}}": 'y',
    r"{\"{A}}": 'A', r"{\"{E}}": 'E', r"{\"{O}}": 'O', r"{\"{U}}": 'U', r"{\"{I}}": 'I', r"{\"{N}}": 'N', r"{\"{Y}}": 'Y',
    r"{\.a}": 'a', r"{\.e}": 'e', r"{\.o}": 'o', r"{\.u}": 'u', r"{\.i}": 'i', r"{\.n}": 'n', r"{\.y}": 'y',
    r"{\.A}": 'A', r"{\.E}": 'E', r"{\.O}": 'O', r"{\.U}": 'U', r"{\.I}": 'I', r"{\.N}": 'N', r"{\.Y}": 'Y',
    r"\v{c}": 'c', r"\v{C}": 'C', r"\v{e}": 'e', r"\v{E}": 'E', r"\v{s}": 's', r"\v{S}": 'S', r"\v{z}": 'z', r"\v{Z}": 'Z',
    r"\"{a}": 'a', r"\"{e}": 'e', r"\"{o}": 'o', r"\"{u}": 'u', r"\"{i}": 'i', r"\"{c}": 'c', r"\"{n}": 'n', r"\"{y}": 'y',
    r"\"{A}": 'A', r"\"{E}": 'E', r"\"{O}": 'O', r"\"{U}": 'U', r"\"{I}": 'I', r"\"{N}": 'N', r"\"{Y}": 'Y',
    r"{\'{\a}}": 'a', r"{\'{\e}}": 'e', r"{\'{\o}}": 'o', r"{\'{\u}}": 'u', r"{\'{\i}}": 'i', r"{\'{\c}}": 'c', r"{\'{\n}}": 'n', r"{\'{\y}}": 'y',
    r"{\'{\A}}": 'A', r"{\'{\E}}": 'E', r"{\'{\O}}": 'O', r"{\'{\U}}": 'U', r"{\'{\I}}": 'I', r"{\'{\N}}": 'N', r"{\'{\Y}}": 'Y', 
    r"{\textquoteright}": "'", r"{\textquotedbl}": '"', r"{\textasciigrave}": "`", r"{\textasciicircum}": "^", r"{\textasciitilde}": "~", r"{\textbackslash}": "\\", r"{\textbar}": "|", r"{\textless}": "<", r"{\textgreater}": ">", r"{\textunderscore}": "_", r"{\textbraceleft}": "{", r"{\textbraceright}": "}", r"{\textbackslash}": "\\",
    "\n": "", "\em": "", "~": " ", "\\&" : "&", "\\$" : "$", "\\%" : "%", "\\#" : "#", "\\_" : "_", "\\{" : "{", "\\}" : "}", "\\textbackslash" : "\\", "\\textasciitilde" : "~", "\\textasciicircum" : "^", "\\textasciigrave" : "`", "\\textquoteright" : "'", "\\textquotedbl" : '"',
    r"{-}": "-",


}

def download_file(url, save_path, overwrite=True): 
    if os.path.exists(save_path) and not overwrite:
        print(f"file {save_path} already exists")
        return False

    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"file {save_path} downloaded")
        return True
    except requests.RequestException as e:
        print(f"Failed to download file from {url}. Error: {e}")
        return False

def unzip_tar_gz(file_path, extract_path):
    try:
        with tarfile.open(file_path, "r:gz") as tar:
            tar.extractall(extract_path)
    except:
        print("unzip error")
        return False

def remove_file(file_path):
    if os.path.exists(file_path):
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
    title = ''
    authors = []
    # print("bib files: ",files)
    if len(files) > 0:
        for file in files:
            with open(file, 'r') as file:
                data = file.read()
            Refs = re.split(r'\n@', data)
            for Ref in Refs:
                Slices = re.split(r',\s*\n', Ref)
                for Slice in Slices:
                    Slice = Slice.strip()
                    if re.match(r'^\s*title\s*=', Slice):
                        cleaned_line = re.sub(r'^title\s*=\s*', '', Slice)
                        cleaned_line = re.sub(r',$', '', cleaned_line)
                        while True:
                            cleaned_line, count1 = re.subn(r'^\{(.*)\}$', r'\1', cleaned_line)
                            cleaned_line, count2 = re.subn(r'^"(.*)"$', r'\1', cleaned_line)
                            if count1 + count2 == 0:
                                break
                        for old, new in replacements.items():
                            cleaned_line = cleaned_line.replace(old, new)
                        cleaned_line = cleaned_line.replace('{', '').replace('}', '')
                        cleaned_line = re.sub(r'\s+', ' ', cleaned_line)
                        title = cleaned_line
                    # elif re.match(r'^\s*author\s*=', Slice):
                    #     cleaned_line = re.sub(r'^author\s*=\s*', '', Slice)
                    #     cleaned_line = re.sub(r',$', '', cleaned_line)
                    #     while True:
                    #         cleaned_line, count1 = re.subn(r'^\{(.*)\}$', r'\1', cleaned_line)
                    #         cleaned_line, count2 = re.subn(r'^"(.*)"$', r'\1', cleaned_line)
                    #         if count1 + count2 == 0:
                    #             break
                    #     for old, new in replacements.items():
                    #         cleaned_line = cleaned_line.replace(old, new)
                    #     cleaned_line = cleaned_line.replace('{', '').replace('}', '')
                    #     cleaned_line = re.sub(r'\s+', ' ', cleaned_line)
                    #     authors = cleaned_line
                    #     authors = authors.split(' and ')
                    #     print(len(authors))
                    #     for i in range(len(authors)):
                    #         if ',' in authors[i]:
                    #             authors[i] = authors[i].split(', ')[1] + ' ' + authors[i].split(', ')[0]
                if title != '' and authors != '' and {'title': title, 'authors': authors} not in ref:
                    # ref.append({'title': title, 'authors': authors})
                    ref.append({'title': title})
                    title = ''
                    authors = []
    
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
                    cleaned_line = newblocks[1].strip()
                    for old, new in replacements.items():
                            cleaned_line = cleaned_line.replace(old, new)
                    cleaned_line = cleaned_line.replace('{', '').replace('}', '')
                    cleaned_line = re.sub(r'.$', '', cleaned_line)
                    cleaned_line = cleaned_line.strip()
                    title = cleaned_line
                    
                    # bbl_author = newblocks[0].strip()
                    # pos = bbl_author.find(']')
                    # if pos != -1:
                    #     bbl_author = bbl_author[pos+1:]
                    # pos = bbl_author.find('}')
                    # if pos != -1:
                    #     cleaned_line = bbl_author[pos+1:]
                    # for old, new in replacements.items():
                    #     cleaned_line = cleaned_line.replace(old, new)
                    # cleaned_line = cleaned_line.replace('{', '').replace('}', '')
                    # cleaned_line = re.sub(r'.$', '', cleaned_line)
                    # authors = re.split(r',\s', cleaned_line)
                    # for i in range(len(authors)):
                    #     authors[i] = authors[i].strip().lstrip("and ").strip()
                    # if title != '' and authors != '' and {'title': title, 'authors': authors} not in ref:
                    if title != '' and {'title': title} not in ref:
                        # ref.append({'title': title, 'authors': authors})
                        ref.append({'title': title})
                        title = ''
                        authors = []
    return ref

def extract_reference(arxiv_id: str):
    save_path = f"./paper/{arxiv_id}"
    files1 = find_bib_files(save_path)
    files2 = find_bbl_files(save_path)
    ref = []
    if len(files2) > 0:
        ref = find_bbl_refs(files2)
    elif len(files1) > 0:
        ref = find_bib_refs(files1)
    return ref

if __name__ == "__main__":
    target=input("input the paper index: ").strip()

    url = f"https://arxiv.org/src/{target}"
    url2= f"https://arxiv.org/pdf/{target}"
    download_path = f"./paper/{target}.tar.gz"
    pdf_path = f"./paper/{target}/{target}.pdf"
    save_path = f"./paper/{target}"
    ref=[]

    if not os.path.exists(save_path):    
        download_file(url, download_path)
        unzip_tar_gz(download_path, save_path)
        download_file(url2, pdf_path)
        remove_file(download_path)
        
    ref = extract_reference(target)

    print("ref count: ",len(ref))
    print("ref list: ")
    for i in ref:
        print(i)
