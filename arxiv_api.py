import urllib.request as libreq

# How to use the arXiv API
# This is file simply for my experiments
if __name__ == '__main__':
    with libreq.urlopen('http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1') as url:
        r = url.read()
    print(r)