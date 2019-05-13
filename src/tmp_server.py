# usr/bin/python27
# author: Seoung H. Song


"""This file has been made up with server.py base"""

from flask import Flask, jsonify, request, render_template
from flask import make_response
from detect import predictor  # Article headline's clickbaitiness predictor
from extract import extractor # Article headline extractor
import logging
import validators
import unicodedata



app = Flask(__name__)


@app.route("/", methods=['GET','POST'])
@app.route("/index", methods=['GET','POST'])
def analyze ():

    if request.method == 'POST':
        sample_url = request.form["sample_url"]
        headline = None
        clickbaitiness = None

        if validators.url(sample_url):
            logging.info("given URL is: {0}".format(sample_url))
            try:
                headline = extractor.extract(sample_url)
            except Exception:
                logging.error("extract headline failed")
                pass

            if headline is not None:
                # logging.info("extracted headline is: {0}".format(headline))

                # try:
                #     # There should be an waiting time for this
                #     clickbaitiness = predictor.predict(headline)
                # except Exception:
                #     logging.error("predict failed")
                #     pass
                headline = unicodedata.normalize('NFKD', headline).encode('ascii','ignore')
                clickbaitiness = predictor.predict(headline)
            else:
                # TODO: return index.html with error flash
                pass
        else:
            # TODO: return index.html with error flash
            logging.error("invalid URL is given")
            pass

        print("===============")
        print(headline)
        print(clickbaitiness)
        print("===============")

        newsinfo = {"headline": headline, "clickbaitiness": round(clickbaitiness, 2)}

        return render_template('index.html', newsinfo=newsinfo)
        # return render_template('index.html', headline, clickbaitiness)
    else:
        return render_template('index.html')



if __name__ == "__main__":
    app.secretKey = 'superSecret'

    # Exporting log history as an external log file
    logging.basicConfig(filename='app.log',
                        filemode='w',
                        datefmt='%d-%b-%y %H:%M:%S',
                        format='%(asctime)s-%(name)s-%(levelname)s-%(message)s')

    app.run(host='127.0.0.1', port=3000, debug=True)
