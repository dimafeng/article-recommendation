import logging

from tenacity import retry, stop_after_attempt, before_log
from article_recs.db.db import Database
from article_recs.target.target import Handler


class MessageHandler(Handler):
    logger = logging.getLogger(__name__)

    def __init__(self, database: Database) -> None:
        self.database = database

# Palogger = logging.getLogger(__name__)
    @retry(stop=stop_after_attempt(3), before=before_log(logger, logging.INFO))
    def handle(self, data: dict) -> None:
        self.database.record_signal("vote", data)