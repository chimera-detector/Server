# usr/bin/python27
# author: Seoung H. Song


"""This file has been made up with server.py base"""

from flask import Flask, jsonify, request, render_template
from flask import make_response
from detect import predictor  # Article headline's clickbaitiness predictor
# from extract import extractor # Article headline extractor
from newspaper import Article
import logging
import validators



app = Flask(__name__)

@app.route("/", methods=["POST"])
@app.route("/index", methods=["POST"])
def analyze ():
    sample_url = request.form["sample_url"]
    headline = None
    clickbaitiness = None

    if validators.url(sample_url):
        logging.info("given URL is: {0}".format(sample_url))
        try:
            headline = extractor(sample_url)
        except Exception:
            logging.error("extract headline failed")
            continue

        if headline is not None:
            logging.info("extracted headline is: {0}".format(headline))

            try:
                # There should be an waiting time for this
                clickbaitiness = predictor.predict(headline)
            except Exception:
                logging.error("predict failed")
                continue
        else:
            # TODO: return index.html with error flash
            continue
    else:
        # TODO: return index.html with error flash
        logging.error("invalid URL is given")
        continue

    print("===============")
    print(headline)
    print(clickbaitiness)
    print("===============")

    return render_template('index.html')
    # return render_template('index.html', headline, clickbaitiness)

# ^^^^^^ Utils below ^^^^^^

def extractor(URL):
    article = Article(URL)
    article.download()
    article.parse()

    return article.title



if __name__ == "__main__":
    app.debug = True

    # Exporting log history as an external log file
    logging.basicConfig(filename='app.log',
                        filemode='w',
                        datefmt='%d-%b-%y %H:%M:%S',
                        format='%(asctime)s-%(name)s-%(levelname)s-%(message)s')

    app.run(host='127.0.0.1', port=3000)
