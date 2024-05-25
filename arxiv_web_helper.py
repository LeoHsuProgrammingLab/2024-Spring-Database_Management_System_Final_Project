from bs4 import BeautifulSoup
import requests

def extract_author(arxiv_id: str):
    url = f"https://arxiv.org/abs/{arxiv_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find the div containing the authors
    authors_div = soup.find('div', class_='authors')
    if (authors_div == None):
        return []

    # Extract all author names
    author_names = [a.text for a in authors_div.find_all('a')]
    return author_names

def extract_title(arxiv_id: str):
    url = f"https://arxiv.org/abs/{arxiv_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find the div containing the title
    title_div = soup.find('h1', class_='title mathjax')
    if (title_div == None):
        return ""
    title_text = title_div.text.replace('Title:', '').strip()

    return title_text

def extract_abstract(arxiv_id: str):
    url = f"https://arxiv.org/abs/{arxiv_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find the div containing the abstract
    abstract_div = soup.find('blockquote', class_='abstract mathjax')
    if (abstract_div == None):
        return ""

    # Extract the text of the abstract
    abstract_text = abstract_div.text.replace('Abstract:', '').strip()
    return abstract_text

if __name__ == "__main__":
    target=input("input the paper index: ").strip()
    author = extract_author(target)
    title = extract_title(target)
    abstract = extract_abstract(target)
    
    print(title)
    print(author)
    print(abstract)
    
