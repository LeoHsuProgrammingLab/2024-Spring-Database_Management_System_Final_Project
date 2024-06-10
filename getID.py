import requests
import concurrent.futures
import re
from tqdm.auto import tqdm
from bs4 import BeautifulSoup

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


# def getId(name):
#     id = ''
#     num = -1
#     href = f'https://arxiv.org/search/?query={name}&searchtype=all&source=header'
#     response = requests.get(href)
#     html = response.text
#     soup = BeautifulSoup(html, 'html.parser')
#     id_elements = soup.select('body > main > div:nth-of-type(2) > ol > li > div > p > a')
#     title_elements = soup.select('body > main > div:nth-of-type(2) > ol > li > p:nth-of-type(1)')
#     for i, element in enumerate(title_elements, start=1):
#         title = element.text
#         cleaned_line = title.strip()
#         for old, new in replacements.items():
#             cleaned_line = cleaned_line.replace(old, new)
#         cleaned_line = re.sub(r'\s+', ' ', cleaned_line)
#         title = cleaned_line.strip()
#         if title.lower() == name.strip().lower():
#             num = i
#             break
#     if num != -1:
#         id_url = id_elements[num - 1]['href']
#         id = id_url.split('/')[-1]   
#     return id

def getId(name):
    id = ''
    href = f'https://arxiv.org/search/?query={name}&searchtype=all&source=header'
    response = requests.get(href)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    id_elements = soup.select('body > main > div:nth-of-type(2) > ol > li > div > p > a')
    title_elements = soup.select('body > main > div:nth-of-type(2) > ol > li > p:nth-of-type(1)')
    for i, element in enumerate(title_elements, start=1):
        title = element.text
        cleaned_line = title.strip()
        for old, new in replacements.items():
            cleaned_line = cleaned_line.replace(old, new)
        cleaned_line = re.sub(r'\s+', ' ', cleaned_line)
        title = cleaned_line.strip()
        if title.lower() == name.strip().lower():
            num = i
            id_url = id_elements[num - 1]['href']
            id = id_url.split('/')[-1]
            break
    return id

def get_Id_by_Title_list(title_list):
    title_and_id_list = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_title = {executor.submit(getId, title): title for title in title_list}
        for future in tqdm(concurrent.futures.as_completed(future_to_title)):
            title = future_to_title[future]
            try:
                id = future.result()
                if id:
                    # title_and_id_list.append((title, id))
                    title_and_id_list.append(id)
            except Exception as e:
                print(f"Error fetching ID for {title}: {e}")
    return title_and_id_list

# def get_Id_by_Title_list(title_list):
#     title_and_id_list = []
#     for ref_title in title_list:
#         id = getId(ref_title)
#         if id != '':
#             # title_and_id_list.append((ref_title, id))
#             title_and_id_list.append(id)
#     return title_and_id_list

if __name__ == "__main__":
    title_list = ['Translating embeddings for modeling multi-relational data', 'Deepdive: Declarative knowledge base construction', 'Metapath2vec: Scalable representation learning for heterogeneous networks', 'Freebase data dumps', 'Openke', 'Yago2: A spatially and temporally enhanced knowledge base from wikipedia', 'DBpedia - a large-scale, multilingual knowledge base extracted from wikipedia', 'Wordnet: A lexical database for english', 'Never-ending learning', 'Holographic embeddings of knowledge graphs', 'Deepwalk: Online learning of social representations', 'Computer science bibliograph, 1996', 'An overview of microsoft academic service (mas) and applications', 'Pte: Predictive text embedding through large-scale heterogeneous text networks', 'Line: Large-scale information network embedding', 'Arnetminer: Extraction and mining of academic social networks', 'Knowledge graph completion via complex tensor factorization', 'Knowledge graph embedding by translating on hyperplanes', 'Embedding entities and relations for learning and inference in knowledge bases']
    title_and_id_list = get_Id_by_Title_list(title_list)
    for i in title_and_id_list:
        print(i)
