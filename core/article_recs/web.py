from fastapi import FastAPI
from pydantic import BaseModel

from article_recs.context import Context

class CheckpointRequest(BaseModel):
    consumer_id: str 
    event_type: str 
    checkpoint: int

class ContentUpdateRequest(BaseModel):
    content_id: str
    data: dict

class CandidateUpdateRequest(BaseModel):
    content_id: str
    scores: dict

class Controller:
    def __init__(self, context: Context):
        self.context = context

        @context.app.get("/")
        def read_root():
            return {"Hello": "World"}

        @context.app.get("/candidates")
        def get_candidates(page: int = 0, limit: int = 10):
            return self.context.database.get_candidates(page, limit)

        @context.app.get("/contents")
        def get_contents(content_ids: str):
            return self.context.database.get_contents(content_ids.split(","))

        @context.app.post("/contents/update")
        def update_contents(request: ContentUpdateRequest):
            self.context.database.update_content(request.content_id, request.data)
            return {"result": "ok"}

        @context.app.get("/signals")
        def get_signals(page: int = 0, limit: int = 10):
            return self.context.database.get_signals(page, limit)

        @context.app.get("/events")
        def get_events(consumer_id: str, event_type: str, limit: int = 10):
            return self.context.database.read_latest_events(consumer_id, event_type, limit, False)

        @context.app.post("/events/checkpoint")
        def checkpoint(checkpoint_request: CheckpointRequest):
            self.context.database.checkpoint(
                checkpoint_request.consumer_id, 
                checkpoint_request.event_type, 
                checkpoint_request.checkpoint
                )
            return {"result": "ok"}

        @context.app.post("/candidates/update")
        def update_candidates(request: CandidateUpdateRequest):
            self.context.database.update_candidate(request.content_id, request.scores)
            return {"result": "ok"}