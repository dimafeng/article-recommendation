import logging
import time
import requests
import json
from sqlalchemy import create_engine
from article_recs.context import Context

from article_recs.db.db import Database
from article_recs.db.models import Base, Content

reddits = [
    'machinelearning',
    'datascience',
    'deeplearning',
    'news',
    'programming',
    'technews',
    'stocks'
]

def main(context: Context):
    logging.info("Starting crawler")

    for reddit in reddits:
        logging.info(f"Crawling https://www.reddit.com/r/{reddit}/top.json?limit=100")
        posts = get_reddit_json(f"https://www.reddit.com/r/{reddit}/top.json?limit=100")

        print(posts)

        for post in posts['data']['children']:
            data = post['data']
            context.database.add_content(Content(
                id="reddit_" + str(data['id']),
                source="reddit_v2",
                title=data['title'],
                url=data['url'],
                data={"reddit_data": data, "type": "external"}
            ))

def get_reddit_json(url):
    data = retry_on_429(get_request_with_user_agent, url).text
    return json.loads(data)

def get_request_with_user_agent(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
    return requests.get(url, headers=headers)

def retry_on_429(func, *args, **kwargs):
    while True:
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logging.info("429 received, sleeping for 5 seconds")
                time.sleep(5)
            else:
                raise e


if __name__ == "__main__":
    main(Context())