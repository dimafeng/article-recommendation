import datetime
from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class Content(Base):
    __tablename__ = "content"

    id = Column(String, primary_key=True)
    source = Column(String) 
    title = Column(String)
    url = Column(String)
    data = Column(JSONB)
    updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    created = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    data = Column(JSONB)
    updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    created = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class EventConsumer(Base):
    __tablename__ = "event_consumers"

    id = Column(String, primary_key=True)
    event_type = Column(String)
    checkpoint = Column(Integer)
    updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    created = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_type = Column(String)
    data = Column(JSONB)
    updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    created = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Candidate(Base):
    __tablename__ = "candidates"

    content_id = Column(String,  primary_key=True)
    scores = Column(JSONB)
    updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    created = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Settings(Base):
    __tablename__ = "settings"

    name = Column(String, primary_key=True)
    value = Column(JSONB)
    updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    created = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)