# usr/bin/python27


import os, sys, re, praw, requests
from datetime import datetime
from bs4 import BeautifulSoup


class Extractor ():
    def __init__(self):
        return None

    def extract (self, URL):
        try:
            res = requests.get(URL)
            if (res.status_code == 200 and 'content-type' in res.headers and res.headers.get('content-type').startswith('text/html')):
                article = parse_article(res.text)
                return article['title']
            else:
                print("failed")
        except Exception:
            pass

    def parse_article(self, text):
        soup = BeautifulSoup(text, "html.parser")

        # find the article title.
        h1 = soup.body.find('h1')

        # find the common parent for <h1> and all <p>s.
        root = h1
        while root.name != 'body' and len(root.find_all('p')) < 5:
            root = root.parent

        if len(root.find_all('p')) < 5:
            return None

        # find all the content elements.
        ps = root.find_all(['h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre'])
        ps.insert(0, h1)
        content = [tag2md(p) for p in ps]

        return {'title': h1.text, 'content': content}


if __name__ == "__main__":
    print("headline is: {0}".format(extractor.extract(sys.argv[1])))
