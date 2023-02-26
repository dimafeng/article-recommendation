from asyncio.log import logger
import time
from article_recs.context import Context
from article_recs.recommenders.scorer import Scorer


def seconds_to_hours(seconds):
    return seconds / 3600

class MostPopularScorer(Scorer):
    def __init__(self, context: Context):
        super().__init__(context)
        self._database = context.database

    def score(self):
        candidates = self._database.get_latest_candidates(500)
        contents = self._database.get_contents([c.content_id for c in candidates])
        for content in contents:
            logger.info(f"Scoring {content.id}")
            if content.source == "hackernews":
                continue
                data = content.data['hackernews_data']
                hn_score = data.get("score", 0)
                time_factor = seconds_to_hours(time.time() - data.get("time", 0)) + 1
                time_weighted_score = hn_score / time_factor

                if data.get("url", None) == None:
                    time_weighted_score = 0

                if data.get("top_image", None) == None:
                    time_weighted_score = time_weighted_score / 2

                self._database.update_candidate(content.id, {"hn_score": hn_score, "time_weighted_score": time_weighted_score})
            if content.source == "reddit_v2":
                data = content.data['reddit_data']
                reddit_score = data.get("score", 0)
                logger.info(f"Reddit score: {reddit_score}")
                time_factor = seconds_to_hours(time.time() - data.get("time", 0)) + 1
                time_weighted_score = reddit_score / time_factor

                if data.get("url", None) == None:
                    time_weighted_score = 0

                if data.get("top_image", None) == None:
                    time_weighted_score = time_weighted_score / 2

                self._database.update_candidate(content.id, {"reddit_score": reddit_score, "time_weighted_score": time_weighted_score})