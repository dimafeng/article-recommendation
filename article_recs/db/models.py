import datetime
from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

# class Value(Base):
#     __tablename__ = "values"

#     id = Column(String, primary_key=True)
#     field_name = Column(String, primary_key=True)
#     string_value = Column(String)
#     int_value = Column(Integer)
#     decimal_value = Column(Numeric)
#     text_value = Column(Text)
#     updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
#     created = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # def __repr__(self):
    #     return "<User(name='%s', fullname='%s', nickname='%s')>" % (
    #         self.name,
    #         self.fullname,
    #         self.nickname,
    #     )

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
