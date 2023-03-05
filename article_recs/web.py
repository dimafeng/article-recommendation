from fastapi import FastAPI
from pydantic import BaseModel

from article_recs.context import Context

class CheckpointRequest(BaseModel):
    consumer_id: str 
    event_type: str 
    checkpoint: int

class Controller:
    def __init__(self, context: Context):
        self.context = context

        @context.app.get("/")
        async def read_root():
            return {"Hello": "World"}

        @context.app.get("/candidates")
        async def get_candidates(page: int = 0, limit: int = 10):
            return self.context.database.get_candidates(page, limit)

        @context.app.get("/contents")
        async def get_contents(content_ids: str):
            return self.context.database.get_contents(content_ids.split(","))

        @context.app.get("/signals")
        async def get_signals(page: int = 0, limit: int = 10):
            return self.context.database.get_signals(page, limit)

        @context.app.get("/events")
        async def get_events(consumer_id: str, event_type: str, limit: int = 10):
            return self.context.database.read_latest_events(consumer_id, event_type, limit, False)

        @context.app.post("/events/checkpoint")
        async def checkpoint(checkpoint_request: CheckpointRequest):
            self.context.database.checkpoint(
                checkpoint_request.consumer_id, 
                checkpoint_request.event_type, 
                checkpoint_request.checkpoint
                )
            return {"result": "ok"}
