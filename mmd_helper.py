import re 
import os
import pandas as pd

def extract_title(mmd):
    title_pattern = r"^# (?!\#)(.+)$"
    match_result = re.search(title_pattern, mmd, re.MULTILINE)

    if match_result:
        return match_result.group(1).strip()
    else:
        print('Title not found')
        return None
    
def extract_abstract(text, max_lines=30):
    # Regex pattern to capture text under the "Abstract" heading until the next heading
    pattern = r"^###### Abstract\.?\s*\n(.*?)(?=\n##|\Z)"
    
    # Search for the pattern
    match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
    
    if match:
        abstract_full = match.group(1).strip()
        # Split the abstract into lines and limit the number of lines returned
        abstract_lines = abstract_full.splitlines()
        limited_abstract = abstract_lines[:max_lines]
        limited_abstract = [line.strip() for line in limited_abstract if line.strip()]
        limited_abstract = '\n'.join(limited_abstract)
        return limited_abstract
    else:
        return "Abstract section not found"
    
def extract_conclusion(mmd):
    # Regex pattern to capture text starting with "##" followed by any characters and "Conclusion"
    # and ending at the next "##" or end of the document
    pattern = r"^## .*?Conclusion.*?\n(.*?)(?=\n##|\Z)"
    
    # Search for the pattern
    match = re.search(pattern, mmd, re.IGNORECASE | re.DOTALL | re.MULTILINE)
    
    if match:
        result = match.group(1).strip().splitlines()
        result = [line.strip() for line in result if line.strip()]
        result = '\n'.join(result)
        return result  # Return the captured group, which is the conclusion
    else:
        return "Conclusion section not found"
    
def extract_content(mmd):
    pattern = r'^##\s*.*?Introduction.*?\n(.*?)(?=\n##|\Z)'
    match = re.search(pattern, mmd, re.IGNORECASE | re.DOTALL | re.MULTILINE)
    
    if match:
        result = match.group(1).strip().splitlines()
        result = [line.strip() for line in result if line.strip()]
        result = '\n'.join(result)
        return result
    else:
        return "Content section not found"
    
def extract_authors(mmd):
    pattern = r'(.*?)###### Abstract'
    match = re.search(pattern, mmd, re.DOTALL)

    author_pattern = r"^[a-zA-Z]+['. -][a-zA-Z ]?[a-zA-Z]*$"

    if match:
        authors = match.group(1).strip().splitlines()
        authors = [author.strip() for author in authors if author.strip()]
        print(authors)
        author_list = []

        for idx, line in enumerate(authors):
            author_match = re.search(author_pattern, line)
            if author_match:
                author_list.append(author_match.group())
                # print("Author not found in line", idx, ":", line)
                
        return author_list
    else:
        return "Authors not found"
    
def extract_keywords(mmd):
    pattern = r'^Keywords.*?\n(.*?)(?=\n\S|\Z)'
    match = re.search(pattern, mmd, re.IGNORECASE | re.DOTALL | re.MULTILINE)
    
    if match:
        result = match.group(1).strip().splitlines()
        result = [line.strip() for line in result if line.strip()]
        result = '\n'.join(result)
        return result
    else:
        return "Keywords section not found"

def main():
    papers = pd.read_csv('./paper/papers.csv')
    arxiv_list = [id[-10:] for id in papers['Arxiv Link'].values]
    for arxiv_id in arxiv_list:
        if os.path.exists(f"./papers/{arxiv_id}/{arxiv_id}.mmd"):
            with open(f"./papers/{arxiv_id}/{arxiv_id}.mmd", 'r') as f:
                mmd = f.read()
            target = extract_keywords(mmd)
            print(arxiv_id, target, '\n')

if __name__ == '__main__':
    main()