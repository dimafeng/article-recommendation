from ctypes import Array
from datetime import datetime, timedelta
import logging
from typing import List
from sqlalchemy import Integer, create_engine
from sqlalchemy import Table, Column, String, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from article_recs.db.models import Base, Candidate, Content, Event, EventConsumer, Settings, Signal


def merge_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


class Database(object):

    def __init__(self, db):
        self.db = db
        self.Session = sessionmaker(bind=db)

    def update_content(self, content_id: str, data: dict):
        with self.Session() as session:
            content = session.query(Content).get(content_id)
            content.data = merge_dicts(content.data, data)
            session.add(Event(type="content_updated", data={
                        "content_id": content.id, "fields": list(data.keys())}))
            session.commit()

    def add_content(self, content: Content):
        with self.Session() as session:
            existing_content = session.query(Content).get(content.id)
            if (existing_content is None):
                logging.info("Adding content %s", content.id)
                session.add(Event(type="content_added",
                            data={"content_id": content.id}))
                session.add(content)
                session.commit()
            else:
                logging.info(
                    "Content %s already exists. Updating...", content.id)
                self.update_content(content.id, content.data)

    def get_latest_content(self, limit: int):
        with self.Session() as session:
            return session.query(Content).order_by(Content.created.desc()).limit(limit).all()

    def get_content(self, content_id: str):
        with self.Session() as session:
            return session.query(Content).get(content_id)

    def get_contents(self, content_ids: List[str]) -> List[Content]:
        with self.Session() as session:
            return session.query(Content).filter(Content.id.in_(content_ids)).all()

    def read_latest_events(self, consumer_id: str, event_type: str, limit: int, save_checkpoint: bool = True):
        if consumer_id is None or consumer_id == "" or event_type is None or event_type == "":
            raise Exception("Invalid consumer_id or event_type")

        with self.Session() as session:
            event_consumers = session.query(EventConsumer).filter(
                EventConsumer.id == consumer_id).all()
            if (len(event_consumers) == 0):
                session.add(EventConsumer(id=consumer_id,
                            event_type=event_type, checkpoint=0))
                event_consumers = session.query(EventConsumer).filter(
                    EventConsumer.id == consumer_id).all()

            event_consumer = event_consumers[0]
            events = session.query(Event).filter(Event.type == event_type).filter(
                Event.id > event_consumer.checkpoint).limit(limit).all()

            if (len(events) == 0):
                session.commit()
                return []

            for e in events:
                session.expunge(e)

            if (save_checkpoint):
                event_consumer.checkpoint = events[-1].id
                session.commit()

            return events

    def checkpoint(self, consumer_id: str, event_type: str, checkpoint: int):
        with self.Session() as session:
            event_consumers = session.query(EventConsumer).filter(
                EventConsumer.id == consumer_id).all()
            if (len(event_consumers) == 0):
                session.add(EventConsumer(id=consumer_id,
                            event_type=event_type, checkpoint=checkpoint))
            else:
                event_consumer = event_consumers[0]
                event_consumer.checkpoint = checkpoint
            session.commit()

    def record_signal(self, signal_type: str, data: dict):
        with self.Session() as session:
            session.add(Signal(signal_type=signal_type, data=data))
            session.add(Event(type="signal", data={
                        "signal_type": signal_type, "data": data}))
            session.commit()

    def get_signals(self, page: int, page_size: int) -> list[Signal]:
        with self.Session() as session:
            return session.query(Signal).order_by(Signal.created.desc()).offset(page * page_size).limit(page_size).all()

    def update_candidate(self, content_id: str, scores: dict):
        with self.Session() as session:
            candidate = session.query(Candidate).get(content_id)
            if candidate is None:
                candidate = Candidate(content_id=content_id, scores=scores)
                session.add(candidate)
            else:
                candidate.scores = merge_dicts(candidate.scores, scores)

            session.commit()

    def delete_candidate(self, content_id: str):
        with self.Session() as session:
            candidate = session.query(Candidate).get(content_id)
            if candidate is not None:
                session.delete(candidate)
                session.commit()

    def get_latest_candidates(self, limit: int):
        with self.Session() as session:
            return session.query(Candidate).order_by(Candidate.created.desc()).limit(limit).all()

    def get_candidates(self, page: int, page_size: int) -> List[Candidate]:
        with self.Session() as session:
            return session.query(Candidate).order_by(Candidate.created.desc()).offset(page * page_size).limit(page_size).all()

    def get_candidates_by_score(self, score_name: str, page: int, page_size: int) -> List[Candidate]:
        with self.Session() as session:
            return session.query(Candidate).order_by(Candidate.scores[score_name].desc()).offset(page * page_size).limit(page_size).all()

    def get_all_candidates(self):
        with self.Session() as session:
            return session.query(Candidate).all()

    def delete_canidates_older_than(self, days: int):
        with self.Session() as session:
            candidates = session.query(Candidate).filter(
                Candidate.created < datetime.now() - timedelta(days=days)).limit(1000).all()
            for candidate in candidates:
                logging.info("Deleting candidate %s", candidate.content_id)
                session.delete(candidate)
            session.commit()

    def delete_oldest_candidates(self, limit: int):
        with self.Session() as session:
            candidates = session.query(Candidate).order_by(
                Candidate.created).limit(limit).all()
            for candidate in candidates:
                session.delete(candidate)
            session.commit()

    def update_settings(self, name: str, value: dict):
        with self.Session() as session:
            settings = session.query(Settings).filter(
                Settings.name == name).first()
            if settings is None:
                settings = Settings(name=name, value=value)
                session.add(settings)
            else:
                settings.value = value
            session.commit()

    def get_settings_by_name(self, name: str, default_value: dict) -> dict:
        with self.Session() as session:
            settings = session.query(Settings).filter(
                Settings.name == name).first()
            if settings is None:
                return default_value
            else:
                return settings.value
