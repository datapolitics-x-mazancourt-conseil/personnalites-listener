#%%
# Imports
from datetime import datetime, timedelta, timezone
import urllib.request
import requests
import os
import json
import logging
import csv
import time
from tweet import Tweet

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

logging.basicConfig(
    filename='logs.log', 
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
)

# connection to elastic search
from elasticsearch_dsl import connections

connection_string = "{url}:{port}".format(
    url=os.environ.get("ELASTIC_URL"), 
    port = os.environ.get("ELASTIC_PORT")
)

connections.create_connection(hosts=[connection_string],http_auth=(os.environ.get("ELASTIC_USERNAME"),os.environ.get("ELASTIC_PWD")))

#%%
# Fonctions utiles
def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

#%%
# Téléchargement

url_candidats = "https://raw.githubusercontent.com/datapolitics/sondages-presidentielles/main/candidats2022.json"
bearer_token = os.environ.get("BEARER_TOKEN")
url_twitter = "https://api.twitter.com/2/tweets/search/recent"
output_file = r"data/fetched_tweets.csv"

keys = [
    "username","author_id","conversation_id","created_at","hashtags",
    "mentions","like_count","quote_count","reply_count", "retweet_count",
    "retweet","reply","quote","reply_settings", "source","text"
]

with urllib.request.urlopen(url_candidats) as f:
    
    candidats = eval(f.read().decode("utf-8"))
    data = []

    # on parcoure l'ensemble des candidats
    for c in candidats[0:1]:
        logging.info("Requesting data for twitter account : {}".format(c["twitter"]))

        # on attend 1 secondes pour s'assurer de rester en dessus du rate limite (de 2 requêtes par seconde)
        time.sleep(1)

        query_string = '(from:{candidat_username})'.format(candidat_username = c["twitter"])

        # on recherche les tweets des dernières 1h05 (soit 1h + petite sécurité)
        # date must be YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339)

        start_time = (datetime.now(timezone.utc) - timedelta(hours=1, minutes=5)).isoformat()
        query_params = {'query': query_string,'start_time':start_time,'tweet.fields': 'attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld'}
        # pour chaque candidat, on fait la requête à l'API Twitter
        json_response = connect_to_endpoint(url_twitter, query_params)

        # on mape les données pour sortir un format à plat
        if('data' in json_response):
            for item in json_response["data"]:

                current_tweet = Tweet()
                current_tweet.id = item["id"]
                current_tweet.username = c["twitter"]
                current_tweet.author_id = item["author_id"]
                current_tweet.conversation_id = item["conversation_id"]
                current_tweet.published = item["created_at"]
                current_tweet.hashtags = [hashtag["tag"] for hashtag in item["entities"]["hashtags"]] if ("entities" in item and "hashtags" in item["entities"]) else None
                current_tweet.mentions = [mention["username"] for mention in item["entities"]["mentions"]] if ("entities" in item and "mentions" in item["entities"]) else None
                current_tweet.like_count = item["public_metrics"]["like_count"]
                current_tweet.quote_count = item["public_metrics"]["quote_count"]
                current_tweet.reply_count = item["public_metrics"]["reply_count"]
                current_tweet.retweet_count = item["public_metrics"]["retweet_count"]
                current_tweet.retweet = (True if any(ref_tweet["type"]=="retweeted" for ref_tweet in item["referenced_tweets"]) else False) if 'referenced_tweets' in item else False
                current_tweet.reply = (True if any(ref_tweet["type"]=="replied" for ref_tweet in item["referenced_tweets"]) else False) if 'referenced_tweets' in item else False
                current_tweet.quote = (True if any(ref_tweet["type"]=="quoted" for ref_tweet in item["referenced_tweets"]) else False) if 'referenced_tweets' in item else False
                current_tweet.reply_settings = item["reply_settings"]
                current_tweet.source = item["source"]
                current_tweet.full_text = item["text"]

                current_tweet.save()
        else:
            logging.info("Aucun tweet pour la personne d'intérêt {}".format(c["twitter"]))
    

