from __future__ import annotations

from typing import Annotated

import pydantic


class ResponseHealth(pydantic.BaseModel):
    status: str
    details: str | None = None


class Response(pydantic.BaseModel):
    success: bool
    message: str


class SearchRequest(pydantic.BaseModel):
    term: Annotated[
        str, pydantic.types.StringConstraints(min_length=2, strip_whitespace=True)
    ]
    k: int = 5


class SnippetOut(pydantic.BaseModel):
    id: int
    title: str
    heading_path: str
    language: str
    code: str
    document_path: str


class SearchResult(pydantic.BaseModel):
    score: float
    snippet: SnippetOut


class ResponseSearch(Response):
    results: list[SearchResult]


class ResponseSyncBody(pydantic.BaseModel):
    document_path: str
    document_sha256: str
    snippets_loaded: int
    snippets_written: int


class ResponseSync(Response):
    sync: ResponseSyncBody | None
    meta: dict[str, str] = {}

