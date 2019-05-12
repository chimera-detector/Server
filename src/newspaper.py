from newsplease import NewsPlease
import sys

class Extractor ():
    def __init__(self):
        greet = "Hello World!!"
        return None

    def extract(self, URL):
        article = NewsPlease.from_url(URL)
        return article.title

extractor = Extractor()

if __name__ == "__main__":
    print("headline is: {0}".format(extractor.extract(sys.argv[1])))
