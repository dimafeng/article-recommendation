import logging
import time
from article_recs.context import Context
from article_recs.db.db import Database
from article_recs.recommenders.most_popular import MostPopularScorer
from article_recs.target.target import Handler

DEFAULT_SETTINGS = [
    {
        "name": "most popular",
        "score_name": "time_weighted_score",
        "emoji": "🔥🧭",
        "number_of_recommendations": 5,
    }
]

def main(context: Context):
    logging.info("Starting message sender")

    context.database.delete_canidates_older_than(4)

    MostPopularScorer(context).score()
    
    candidates = context.database.get_all_candidates()         
    
    settings = context.database.get_settings_by_name("recommender_settings", DEFAULT_SETTINGS)
    
    for setting in settings:
        candidates = sort_candidates_by_score(candidates)

        candidates_to_send = candidates[:setting["number_of_recommendations"]]
        for candidate in candidates_to_send:
            send_message(context, candidate.content_id, setting["emoji"])
            context.database.update_content(candidate.content_id, {
                "sent": True, 
                "sent_at": time.time(), 
                "sent_recommender": setting["name"], 
                "sent_recommender_score": candidate.scores.get(setting["score_name"], 0)
                })
            context.database.delete_candidate(candidate.content_id)
        
        candidates = candidates[setting["number_of_recommendations"]:]



def sort_candidates_by_score(candidates, score_name="time_weighted_score"):
    return sorted(candidates, key=lambda c: c.scores.get(score_name, 0), reverse=True)

def send_message(context: Context, content_id: str, emoji: str = ""):
    content = context.database.get_content(content_id)
                
    image = content.data.get("top_image", None)
    summary = shorten_text(content.data.get("summary", None), 400)

    logging.info("Sending message")
    text = f"{emoji} {content.title}"
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