from typing import Annotated

import pydantic

from app.vector import _SearchResult


class ResponseHealth(pydantic.BaseModel):
    status: str
    details: str | None = None


class Response(pydantic.BaseModel):
    success: bool
    message: str


class ResponseSyncBody(pydantic.BaseModel):
    id: int
    status: str
    records_processed: int
    # started_at: int
    # finished_at: int
    # duration_seconds: int


class ResponseSync(Response):
    sync: ResponseSyncBody | None
    meta: dict[str, str]


class ResponseSearch(Response):
    results: list[_SearchResult]


class SearchRequest(pydantic.BaseModel):
    term: Annotated[
        str, pydantic.types.StringConstraints(min_length=2, strip_whitespace=True)
    ]
