import urllib.request as libreq

if __name__ == '__main__':
    with libreq.urlopen('http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1') as url:
        r = url.read()
    print(r)