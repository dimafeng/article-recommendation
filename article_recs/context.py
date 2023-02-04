import logging
import os
import threading
from sqlalchemy import create_engine

from article_recs.db.db import Database
from article_recs.db.models import Base
from article_recs.target.message_handler import MessageHandler
from article_recs.target.target import Target
from article_recs.target.telegram import TelegramTarget

def convert_file_path_to_absolute_path(path):
    if path.startswith("~"):
        return os.path.expanduser(path)
    return path

def read_application_config_json_to_env():
    import json
    config_path = convert_file_path_to_absolute_path("~/article_rec.json")
    
    if not os.path.exists(config_path):
        logging.warning("No config file found at %s", config_path)
        return

    with open(config_path, "r") as f:
        config = json.load(f)
        for key, value in config.items():
            os.environ[key] = value

class Context:

    def __init__(self) -> None:
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(module)s: %(message)s', level=logging.INFO)
        logging.info("Starting application")
        
        read_application_config_json_to_env()

        self.db_string = os.environ.get("POSTGRES_CONNECTION", "postgresql://postgres:example@localhost/recs")
        self.db = create_engine(self.db_string)

        with self.db.connect() as conn:

            Base.metadata.create_all(self.db)

        self.database = Database(self.db)
        self.messageHandler = MessageHandler(self.database)
        token = os.environ.get("TELEGRAM_TOKEN", "")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

        self.telegram_target = TelegramTarget(token, chat_id, self.messageHandler)

    def start_telegram_target(self):
        self.telegram_target.start()

    