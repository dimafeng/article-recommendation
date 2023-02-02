import logging
import time
import requests
from sqlalchemy import create_engine
from article_recs.context import Context

from article_recs.db.db import Database
from article_recs.db.models import Base, Content


def main(context: Context):
    logging.info("Starting crawler")

    r = requests.get(
        'https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty')
    
    for article_id in r.json():
        logging.debug("Crawling article %s", article_id)

        article = requests.get(
            f'https://hacker-news.firebaseio.com/v0/item/{article_id}.json?print=pretty').json()

        context.database.add_content(Content(
            id="hackernews" + str(article_id),
            source="hackernews",
            title=article['title'],
            url=article.get('url', ''),
            data={"hackernews_data": article}
        ))

if __name__ == "__main__":
    main(Context())
