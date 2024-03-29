import logging
import os
import threading
from fastapi import FastAPI
from sqlalchemy import create_engine
from article_recs.content_extraction.scraper import PaywallScraperStrategy, SeleniumScraper, SimpleScraper

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
        #logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
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

        selenium_url = os.environ.get("SELENIUM_URL", "http://localhost:4444/wd/hub")

        selenium_scraper = SeleniumScraper(selenium_url)
        simple_scraper = SimpleScraper()
        self.scraper = PaywallScraperStrategy(simple_scraper, selenium_scraper)

        self.app = FastAPI()

        if token == "" or chat_id == "":
            logging.warning("No telegram token or chat id found")
            self.telegram_target = None
        else:
            self.telegram_target = TelegramTarget(token, chat_id, self.messageHandler)

        # configs
        self.enable_background_tasks = os.environ.get("ENABLE_BACKGROUND_TASKS", "true") == "true"

    def start_telegram_target(self):
        self.telegram_target.start()
