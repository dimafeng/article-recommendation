import logging
import time
from article_recs.context import Context


def main(context: Context):
    i = 0
    while i < 5: 
        events = context.database.read_latest_events("candidate_generator", "content_updated", 100)
        if len(events) == 0:
            logging.info("No new events")
            return

        for event in events:
            content = context.database.get_content(event.data["content_id"])
            if not content == None and content.data.get("sent", None) == None:
                context.database.update_candidate(event.data["content_id"], {})
        
        i += 1


if __name__ == "__main__":
    main(Context())

