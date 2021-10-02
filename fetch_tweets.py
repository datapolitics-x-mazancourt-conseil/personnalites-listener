#%%
# Imports
import urllib.request
import requests
import os
import json
import logging
import csv
import time

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

logging.basicConfig(
    filename='logs.log', 
    encoding='utf-8', 
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
)

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
    for c in candidats:
        logging.info("Requesting data for twitter account : {}".format(c["twitter"]))

        # on attend 1 secondes pour s'assurer de rester en dessus du rate limite (de 2 requêtes par seconde)
        time.sleep(1)

        query_string = '(from:{candidat_username}) OR #twitterdev'.format(candidat_username = c["twitter"])
        query_params = {'query': query_string,'tweet.fields': 'attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld'}

        # pour chaque candidat, on fait la requête à l'API Twitter
        json_response = connect_to_endpoint(url_twitter, query_params)
        print(json.dumps(json_response, indent=4, sort_keys=True))

        # on mape les données pour sortir un format à plat
        for item in json_response["data"]:
            data.append(
                {
                    keys[0]:c["twitter"],
                    keys[1]:item["author_id"],
                    keys[2]:item["conversation_id"],
                    keys[3]:item["created_at"],
                    keys[4]:[hashtag["tag"] for hashtag in item["entities"]["hashtags"]] if ("entities" in item and "hashtags" in item["entities"]) else None,
                    keys[5]:[mention["username"] for mention in item["entities"]["mentions"]] if ("entities" in item and "mentions" in item["entities"]) else None,
                    keys[6] : item["public_metrics"]["like_count"],
                    keys[7] : item["public_metrics"]["quote_count"],
                    keys[8] : item["public_metrics"]["reply_count"],
                    keys[9] : item["public_metrics"]["retweet_count"],
                    keys[10] : (True if any(ref_tweet["type"]=="retweeted" for ref_tweet in item["referenced_tweets"]) else False) if 'referenced_tweets' in item else False,
                    keys[11] : (True if any(ref_tweet["type"]=="replied" for ref_tweet in item["referenced_tweets"]) else False) if 'referenced_tweets' in item else False,
                    keys[12] : (True if any(ref_tweet["type"]=="quoted" for ref_tweet in item["referenced_tweets"]) else False) if 'referenced_tweets' in item else False,
                    keys[13]: item["reply_settings"],
                    keys[14]: item["source"],
                    keys[15]: item["text"]
                }
            )


with open(output_file,"w+") as f:
    writer = csv.DictWriter(f, fieldnames=keys)
    writer.writeheader()
    [writer.writerow(row) for row in data]
        

