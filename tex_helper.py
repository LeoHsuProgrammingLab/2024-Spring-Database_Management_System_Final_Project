import re 

def extract_by_label(tex, label):
    if label[-1] == '*':
        label = label[:-1] + '\*'
    
    pattern = r'\\' + label + r'\{(.|\r|\n)*\}'
    pattern = re.compile(r'\\' + label + r'\{([^}]*)\}')
    # print(pattern)

    match_result = pattern.findall(tex)
    return match_result[0]

def extract_begin_end(tex, keyword):
    pattern = re.compile(r'\\begin\{' + keyword + r'\}(.*?)\\end\{' + keyword + r'\}', re.DOTALL)
    return pattern.findall(tex)

def extract_conclusion(tex):
    match_result = re.search(r'\\section\*\{([a-zA-Z0-9. ]*conclusion[a-zA-Z0-9. ]*)\}(.*?)\\section\*\{(.*?)\}', tex, re.DOTALL|re.IGNORECASE)
    return match_result.groups()[1]

def extract_authors(tex):
    match_result = re.search(r'\\author\{(.*?)\}', tex, re.DOTALL)
    return match_result.groups()[0].split('\n')[0].strip('\\').split(', ')

def extract_content(tex):
    match_result = re.search(r'\\section\*\{([a-zA-Z0-9. ]*introduction[a-zA-Z0-9. ]*)\}(.*?)\\section\*\{([a-zA-Z0-9. ]*reference[a-zA-Z0-9. ]*)\}', tex, re.DOTALL|re.IGNORECASE)
    content = match_result.group()
    
    for idx in range(1, len(content)):
        if content[-idx] == '\n':
            content = content[:-idx]
            return content

def extract_ref_title(ref):
    pattern = r'\[[0-9]+\] (.*?)(\d{4}|\[n\. d\.\]). (.*?)\.'
    match_result = re.search(pattern, ref)
    # authors_part = match_result.group(1).strip()[:-1]
    return match_result.group(3)

    # Split authors by common delimiters and clean up the results
    # authors = re.split(r',\s*|\band\b', authors_part)
    # authors = [author.strip() for author in authors if author.strip()]
    # if authors[-1] == 'et al':
    #     authors = authors[:-1]
    # return authors

def extract_reference(tex):
    pattern = r'\\section\*\{REFERENCES\}(.*?)(?=\\end\{document\}|$)'
    match_result = re.search(pattern, tex, re.I|re.DOTALL)
    reference = match_result.group(1).strip().split('\n\n')
    
    return [extract_ref_title(ref) for ref in reference]
        

if __name__ == '__main__':
    with open('test.tex', 'r') as f:
        tex = f.read()
    conclusion = extract_reference(tex)
    print(conclusion)