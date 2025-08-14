from abc import ABC, abstractmethod
from enum import Enum
from typing import Annotated, override

import pydantic
import requests
from markdown import Markdown

from app.exceptions import FailedGistParseError, FailedGistRequestError
from app.markdown import ParseMarkdown


class SnippetLanguages(Enum):
    python = "python"
    typescript = "typescript"

    def __str__(self) -> str:
        return self.value


class Snippet(pydantic.BaseModel):
    language: SnippetLanguages
    code: str
    details: Annotated[list[str], pydantic.Field(min_length=1)]

    def __str__(self) -> str:
        r = f"{self.language} {self.code} {' '.join([s for s in self.details])}"
        r = f"{self.language} {' '.join([s for s in self.details])}"
        return r
        # return details + " ".join(
        #     [str(v) for k, v in self.model_dump().items() if k != "details"]
        # )


class SnippetSource(ABC):
    @abstractmethod
    async def get_snippets(self) -> list[Snippet]: ...


class SnippetGist(SnippetSource):
    gist_id: str
    comments_endpoint = "comments"
    gist_url = "https://gist.githubusercontent.com/khansgithub/{gist_id}/raw"
    gist_comments_url = "https://api.github.com/gists/{gist_id}/comments"
    markdown_factory = lambda _: Markdown(extensions=["toc", "fenced_code"])

    def __init__(self, gist_id: str) -> None:
        self.gist_id = gist_id
        super().__init__()

    def get_gist(self):
        url = self.gist_url.format(self.gist_id)
        try:
            res = requests.get(url)
        except requests.exceptions.RequestException as e:
            raise FailedGistRequestError(url, None, msg="Failed to get gist") from e

        if res.status_code != requests.codes.ok:
            raise FailedGistRequestError(
                url, res, msg=f"Status code is not 200: {res.status_code}"
            )

        if len(res.text) < 2:
            raise FailedGistRequestError(
                url, res, msg=f"Response text is malformed: length = {len(res.text)}"
            )

        self.parse_markdown(res.text)

    def parse_markdown(self, raw_text: str):
        parser = ParseMarkdown(raw_text)
        try:
            md = parser.parse_markdown()
        except Exception as e:
            raise FailedGistParseError(f"Could not parse raw text: {raw_text=}") from e


class SnippetFile(SnippetSource): ...


class SnippetRaw(SnippetSource):
    @override
    async def get_snippets(self) -> list[Snippet]:
        return [
            Snippet(
                language=SnippetLanguages.python,
                code="...",
                details=["first line of details", "second line of details"],
            ),
            Snippet(
                language=SnippetLanguages.python,
                code=r"set FILE=config.py && isort %FILE%  && black %FILE% && ruff check %FILE% --fix  && mypy %FILE%",
                details=["lint + formatting", "poetry add -D black ruff pylint isort"],
            ),
            Snippet(
                language=SnippetLanguages.python,
                code="""
import sys
from unittest.mock import MagicMock

mod = None
missing_mod = False

while missing_mod:
    if mod:
        print("Adding: " + mod)
        sys.modules[mod] = MagicMock()
        mod = False
    try:
        # import lines go here
    except ModuleNotFoundError as e:
        mod = e.msg.split(" ")[3].translate(str.maketrans('','','";\''))
        print("Missing: " + mod)
        missing_mod = True
        # input("> ")
# sys.exit(0)
# resume rest of the code
""",
                details=["mock all missing imports dynamically"],
            ),
            Snippet(
                language=SnippetLanguages.python,
                code="""
async def SSEStream(request: HttpRequest):
    async def stream():
        _cached_count = None
        while True:
            _cached_count = count
            yield (
                'event: event name'
                '\n'
                f'data: data'
                '\n\n' # <- must be 2 new lines to end a message
            )
        await sleep(1.0)
    return StreamingHttpResponse(stream(), content_type='text/event-stream')

# usage: urls.py
urlpatterns =  [path('stream', SSEStream, name='stream')]
""",
                details=["server event stream in django"],
            ),
        ]
