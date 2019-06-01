# usr/bin/python27
# author: Seoung H. Song


"""This file has been made up with server.py base"""

from flask import Flask, jsonify, request, render_template
from flask import make_response
from detect import detector  # Article headline's clickbaitiness predictor
from tmp_predict import predictor # Article stance detector
from extract import extractor # Article headline extractor
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Clickbait, Stance
import logging
import validators
import unicodedata
import csv



app = Flask(__name__)

# allow all domains can get the response from this server.
CORS(app)

# Connect to database
engine = create_engine('sqlite:///cnn.db')
Base.metadata.bind = engine

# Create session
DBSession = sessionmaker(bind=engine)
session = DBSession()

# analyze def() is just for testing website (currently, clickbaitiness checking)
@app.route("/", methods=['GET','POST'])
@app.route("/index", methods=['GET','POST'])
def analyze ():

    if request.method == 'POST':
        sample_url = request.form["sample_url"]
        headline = None
        clickbaitiness = None

        if validators.url(sample_url) and sample_url is not "":
            try:
                article = extractor.extract(sample_url)

                headline = article['title']
            except Exception:
                logging.error("extract headline failed")
                pass

            if headline is not None:
                clickbaitiness = detector.detect(headline)

                row = [headline, clickbaitiness] # For extracting as csv file
                try:
                    SetToFile(row)
                except Exception:
                    logging.error("store as file failed")
                    pass
            else:
                # TODO: return index.html with error flash
                pass
        else:
            # TODO: return index.html with error flash
            logging.error("invalid URL is given")
            pass

        if headline is not None and clickbaitiness is not None:
            newsinfo = {"headline": headline, "clickbaitiness": round(clickbaitiness, 2)*100}
        else:
            newsinfo = None

        return render_template('index.html', newsinfo=newsinfo)
    else:
        return render_template('index.html')


@app.route("/detect", methods=["GET"])
def detect ():
    headline = request.args.get("headline", "")
    clickbaitiness = detector.detect(headline)

    # push clickbaitiness information into DB
    newArticle = Clickbait(title=headline,
                           clickbaitiness=clickbaitiness)

    session.add(newArticle)
    session.commit()

    # TODO: Store headlines and their clickbaitiness results as external file.
    return jsonify({ "clickbaitiness": round(clickbaitiness * 100, 2) })


@app.route("/predict", methods=["GET"])
def predict ():
    url = request.args.get("URL", "")

    headline = None
    content = None
    stance = None

    if validators.url(url) and url is not "":
        try:
            article = extractor.extract(url)

            headline = article['title']
            content = article['content']

            # push stance information into DB
            newArticle = Stance(title=headline,
                                content=content)

            session.add(newArticle)
            session.commit()

        except Exception:
            logging.error("extract headline failed")
            pass

        if headline is not None and content is not None:

            predictor.save_testData(headline, content)
            stance = predictor.predict(headline, content)

            row = [headline, stance] # For extracting as csv file
            try:
                SetToFile(row)
            except Exception:
                logging.error("store as file failed")
                pass

            if stance is not None:
                return jsonify({ "stance": stance})
            else:
                return jsonify({ "stance": ""})
        else:
            # TODO: return index.html with error flash
            pass
    else:
        logging.error("invalid URL is given")
        pass


def SetToFile(row):
    # Assume that we already know the structure of csv file
    # Appending following row
    flag = False
    headlines = []

    with open('news.csv', 'r') as readFile:
        reader = csv.reader(readFile)
        lines = list(reader)
        # print(lines)

        for line in lines:
            flag = (row[0] == line[0])
            headlines.append(flag)


        if True not in headlines:
            with open('news.csv', 'a') as appendFile:
                writer = csv.writer(appendFile)
                writer.writerow(row)

            appendFile.close()
        else:
            logging.error("headline is already exists")

    readFile.close()


def getClickbait(article_id):
    article = session.query(Clickbait).filter_by(id=article_id).one()
    return article


def getStance(article_id):
    article = session.query(Stance).filter_by(id=article_id).one()
    return article


def getClickbaitAll():
    articles = session.query(Clickbait)
    return articles


def getStanceAll():
    articles = session.query(Stance)
    return articles



if __name__ == "__main__":
    app.secretKey = 'superSecret'

    # Exporting log history as an external log file
    logging.basicConfig(filename='app.log',
                        filemode='w',
                        datefmt='%d-%b-%y %H:%M:%S',
                        format='%(asctime)s-%(name)s-%(levelname)s-%(message)s')

    app.run(host='127.0.0.1', port=3000, debug=True, ssl_context=('cert.pem', 'key.pem'))