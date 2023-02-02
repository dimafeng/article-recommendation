import logging
import time
from article_recs.context import Context
from article_recs.db.models import Content


from newspaper import Article


def extract_text(content: Content, context: Context):
    if (content.url == ""):
        return
    
    logging.info()

    article = Article(content.url)
    try:
        article.download()
        article.parse()
        article.nlp()
    except:
        logging.error("Error while downloading article %s", content.url)
        return

    data = {}
    if (article.publish_date != None):
        data["publish_date"] = article.publish_date.isoformat()

    if (article.text != None):
        data["text"] = article.text

    if (article.top_image != None):
        data["top_image"] = article.top_image

    if (article.keywords != None): 
        data["keywords"] = article.keywords
    
    if (article.summary != None):
        data["summary"] = article.summary

    context.database.update_content(content.id, data)


def main(context: Context):
    logging.info("Starting content extractor")

    events = context.database.read_latest_events("content_extractor", "content_added", 100)
    if len(events) == 0:
        logging.info("No new events")
        return

    for event in events:
        content_id = event.data["content_id"]
        content = context.database.get_content(content_id)
        try:
            extract_text(content, context)
        except Exception as e:
            logging.error("Error while extracting text for", content_id, e)




if __name__ == "__main__":
    main(Context())