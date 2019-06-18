# usr/bin/python27
# author: Seoung H. Song


"""This file has been made up with server.py base"""

from flask import Flask, jsonify, request, render_template
from flask import make_response, send_file
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
engine = create_engine('sqlite:///cnn.db?check_same_thread=False')
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
                    SaveToFile(row)
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
            # newsInfo = {"headline": headline, "clickbaitiness": round(clickbaitiness, 2)*100}
            newsInfo = {"headline": headline, "clickbaitiness": clickbaitiness}

            """ Test Zone"""
            pushToDB(newsInfo)

            return render_template('index.html', headline=newsInfo['headline'], cb_result=round(newsInfo['clickbaitiness'], 2)*100)
        else:
            newsInfo = None
            return render_template('index.html')
    else:
        return render_template('index.html')


@app.route("/dashboard", methods=["GET"])
def show_dashboard():
    try:
        # initial dummy values prior to add existing number of articles
        clickbait = 2390
        agree = 182
        disagree = 8147
        discuss = 2413
        unrelated = 17281

        # TODO: need to add items from DB

        return render_template('dashboard.html', clickbait=clickbait, agree=agree, disagree=disagree, discuss=discuss, unrelated=unrelated)
    except:
        logging.error("dashboard view get me an error")
        return render_template('errors.html')


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
    exist_flag = False

    if validators.url(url) and url is not "":
        try:
            article = extractor.extract(url)

            headline = article['title']
            content = article['content']

        except Exception:
            logging.error("extract headline failed")
            pass

        if headline is not None and content is not None:

            exist_flag = is_headline_duplicated_stance(headline)
            if (exist_flag): # If True, then return the same stance value what already been stored
                if headline is not None:
                    query = session.query(Stance).filter_by(title=headline).one()
                    if query is not None:
                        stance = query.stance
                    else:
                        logging.error("Empty headline is given")
                        pass
            else:

                predictor.save_testData(headline, content)
                stance = predictor.predict(headline, content)

                # push stance information into DB
                newsInfo = {"headline": headline, "content": content, "stance": stance}
                pushToDB(newsInfo)

                row = [headline, stance] # For extracting as csv file
                try:
                    SaveToFile(row)
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



""" ========== API =========== """


@app.route("/api/download/<path>")
def downloadFile(path = None):
    if path is None:
        self.error(400)
    try:
        return send_file(path, as_attachment=True)
    except:
        self.log.exception(e)
        self.Error(400)


# Purpose of getClickbait: return all the queries what the clickbait table has.
@app.route("/json/clickbaits", methods=["GET"])
def cb_result ():
    queries = getClickbaitAll()
    # TODO: this function need to return the list of json object
    return jsonify(result = [q.serialize for q in queries])


# Purpose of getClickbait: return all the queries what the clickbait table has.
@app.route("/json/stances", methods=["GET"])
def st_result ():
    queries = getStanceAll()
    # TODO: this function need to return the list of json object
    return jsonify(result = [q.serialize for q in queries])



""" ========== Utils =========== """


def SaveToFile(row):
    # Assume that we already know the structure of csv file
    # Appending following row
    flag = False
    headlines = []

    if len(row) < 3:
        with open('clickbait.csv', 'r') as readFile:
            reader = csv.reader(readFile)
            lines = list(reader)

            # Duplication article headline checking
            for line in lines:
                flag = (row[0] == line[0])
                headlines.append(flag)


            if True not in headlines:
                with open('clickbait.csv', 'a') as appendFile:
                    writer = csv.writer(appendFile)
                    writer.writerow(row)

                appendFile.close()
            else:
                logging.error("headline exists on clickbait file")

        readFile.close()
    else:
        with open('stance.csv', 'r') as readFile:
            reader = csv.reader(readFile)
            lines = list(reader)

            # Duplication article headline checking
            for line in lines:
                flag = (row[0] == line[0])
                headlines.append(flag)


            if True not in headlines:
                with open('stance.csv', 'a') as appendFile:
                    writer = csv.writer(appendFile)
                    writer.writerow(row)

                appendFile.close()
            else:
                logging.error("headline exists on stance file")

        readFile.close()


# pushToDB function will push newsInfo into DB properly regardless the type of Info
def pushToDB(newsInfo):
    newArticle = None
    duplication_flag = False

    print(newsInfo)

    if "stance" in newsInfo.keys() :
        duplication_flag = is_headline_duplicated_stance(newsInfo["headline"])
        if duplication_flag is False :
            newArticle = Stance(title=newsInfo["headline"],
                                content=newsInfo["content"],
                                stance=newsInfo["stance"])

            session.add(newArticle)
            session.commit()
            print("Clickbait result has been added into DB!!")
        else:
            print("headline exists")
    else:
        duplication_flag = is_headline_duplicated_clickbait(newsInfo["headline"])
        if duplication_flag is False :
            newArticle = Clickbait(title=newsInfo["headline"],
                                   clickbaitiness=newsInfo["clickbaitiness"])

            session.add(newArticle)
            session.commit()
            print("Stance result has been added into DB!!")
        else:
            print("headline exists")


def is_headline_duplicated_clickbait(headline):
    if headline is not None:
        queries = session.query(Clickbait).filter_by(title=headline).all()
        if len(queries) > 0:
            return True
        else:
            return False

def is_headline_duplicated_stance(headline):
    if headline is not None:
        queries = session.query(Stance).filter_by(title=headline).all()
        if len(queries) > 0:
            return True
        else:
            return False



# note that below functions return `Object`
def getClickbait(article_id):
    article = session.query(Clickbait).filter_by(id=article_id).one()
    return article


def getStance(article_id):
    article = session.query(Stance).filter_by(id=article_id).one()
    return article


def getClickbaitAll():
    articles = session.query(Clickbait).all()
    return articles


def getStanceAll():
    articles = session.query(Stance).all()
    return articles



if __name__ == "__main__":
    app.secretKey = 'superSecret'

    # Exporting log history as an external log file
    logging.basicConfig(filename='app.log',
                        filemode='w',
                        datefmt='%d-%b-%y %H:%M:%S',
                        format='%(asctime)s-%(name)s-%(levelname)s-%(message)s')

    app.run(host='127.0.0.1', port=3000, debug=True, ssl_context=('cert.pem', 'key.pem'))
