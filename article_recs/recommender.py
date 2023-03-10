import logging
import time
from article_recs.context import Context
from article_recs.db.db import Database
from article_recs.recommenders.most_popular import MostPopularScorer
from article_recs.target.target import Handler

def main(context: Context):
    logging.info("Starting message sender")

    context.database.delete_canidates_older_than(4)

    MostPopularScorer(context).score()
    
    candidates = context.database.get_all_candidates()         
    candidates = sort_candidates_by_score(candidates)

    for candidate in candidates[:5]:
        send_message(context, candidate.content_id)
        context.database.update_content(candidate.content_id, {"sent": True})
        context.database.delete_candidate(candidate.content_id)


def sort_candidates_by_score(candidates):
    return sorted(candidates, key=lambda c: c.scores.get("time_weighted_score", 0), reverse=True)

def send_message(context: Context, content_id: str):
    content = context.database.get_content(content_id)
                
    image = content.data.get("top_image", None)
    summary = shorten_text(content.data.get("summary", None), 400)

    logging.info("Sending message")
    text = f"{content.title}"
    if summary != None:
        text += f"\n\n{summary}"
    text += f"\n\n{content.url}"

    context.telegram_target.send(content_id, text, image)

def shorten_text(text, max_length):
    if text == None:
        return ""

    if len(text) > max_length:
        return text[:max_length] + "..."

    return text

if __name__ == "__main__":
    main(Context())