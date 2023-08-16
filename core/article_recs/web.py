from typing import List, Optional
import strawberry

from fastapi import FastAPI
from pydantic import BaseModel
from strawberry.fastapi import BaseContext, GraphQLRouter
from strawberry.types import Info
from strawberry.scalars import JSON, ID
from strawberry.dataloader import DataLoader
from starlette.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

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

        origins = [
            "http://localhost",
            "http://localhost:3000",
        ]

        context.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        schema = strawberry.Schema(query=Query, mutation=Mutation)

        graphql_app = GraphQLRouter(
            schema, context_getter=lambda: CustomContext(self.context))

        context.app.include_router(graphql_app, prefix="/graphql")

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
            self.context.database.update_content(
                request.content_id, request.data)
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
            self.context.database.update_candidate(
                request.content_id, request.scores)
            return {"result": "ok"}


class CustomContext(BaseContext):
    def __init__(self, context: Context):
        self.context = context
        self.content_loader = DataLoader(load_fn=content_loader(context))


def content_loader(context: Context):
    async def load_content(keys: List[str]) -> List[Content]:
        content_list = await run_in_threadpool(context.database.get_contents, keys)
        return map(content_model_to_graphql, content_list)
    return load_content


@strawberry.type
class ContentData:
    sent: Optional[bool]
    text: Optional[str]
    summary: Optional[str]
    top_image: Optional[str]
    keywords: Optional[List[str]]
    html: Optional[str]


@strawberry.type
class Content:
    id: ID
    source: str
    title: str
    url: str
    data: ContentData


@strawberry.type
class Candidate:
    content_id: str
    scores: JSON

    @strawberry.field
    async def content(self, info: Info) -> Content:
        return await info.context.content_loader.load(self.content_id)


@strawberry.type
class Settings:
    name: str
    value: JSON


def content_model_to_graphql(content) -> Content:
    return Content(
        id=content.id,
        source=content.source,
        title=content.title,
        url=content.url,
        data=ContentData(
            sent=content.data.get("sent", None),
            text=content.data.get("text", None),
            summary=content.data.get("summary", None),
            top_image=content.data.get("top_image", None),
            keywords=content.data.get("keywords", None),
            html=content.data.get("html", None),
        )
    )


@strawberry.type
class Query:
    @strawberry.field
    def candidates(self, page: int, page_size: int, info: Info, score_name: str | None = None) -> List[Candidate]:
        context: Context = info.context.context

        if score_name:
            return context.database.get_candidates_by_score(
                score_name, page, page_size)  # type: ignore

        return context.database.get_candidates(page, page_size)

    @strawberry.field
    def contents(self, content_ids: List[str], info: Info) -> List[Content]:
        context: Context = info.context.context
        content_list = context.database.get_contents(content_ids)
        return map(content_model_to_graphql, content_list)

    @strawberry.field
    def settings(self, name: str, info: Info) -> JSON:
        context: Context = info.context.context

        return context.database.get_settings_by_name(name, None)


@strawberry.type
class Mutation:
    @strawberry.mutation
    def update_settings(self, name: str, value: JSON, info: Info) -> JSON:
        context: Context = info.context.context

        context.database.update_settings(name, value)

        return value
