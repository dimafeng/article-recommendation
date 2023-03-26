import logging

from article_recs.context import Context
from article_recs.db.models import Content


def extract_text(content: Content, context: Context):
    if (content.url == ""):
         return
    
    context.scraper.load(content.url)

    data = context.scraper.get_meta_data()
    logging.info(f"Extracted text for {content.id}: {data}")
    
    data["text"] = context.scraper.get_plain_text()
    data["html"] = context.scraper.get_article_html()

    context.database.update_content(content.id, data)


def main(context: Context):
    logging.info("Starting content extractor")

    events = context.database.read_latest_events("content_extractor_test", "content_added", 30)
    if len(events) == 0:
        logging.info("No new events")
        return

    for event in events:
        content_id = event.data["content_id"]
        content = context.database.get_content(content_id)
        try:
            extract_text(content, context)
        except Exception as e:
            logging.error(f"Error while extracting text for {content_id}: {str(e)}")




if __name__ == "__main__":
    main(Context())