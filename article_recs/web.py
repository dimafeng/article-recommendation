from fastapi import FastAPI

from article_recs.context import Context


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