from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Annotated, Never, override

import pydantic
import requests

from app.exceptions import (
    FailedGistFileOpenError,
    FailedGistParseError,
    FailedGistRequestError,
)
from app.markdown import ParseMarkdown
from app.utils import Index
from app.app_logging import logger
logger = logger.getChild(__name__)


class SnippetLanguages(Enum):
    python = "python"
    typescript = "typescript"

    def __str__(self) -> str:
        return self.value


class Snippet(pydantic.BaseModel):
    language: SnippetLanguages | str
    # code: str
    code: list[str] | str
    details: Annotated[list[str], pydantic.Field(min_length=1)]
    title: str

    def __str__(self) -> str:
        # r = f"{self.language} {self.code} {' '.join([s for s in self.details])}"
        # r = f"{self.language} {' '.join([s for s in self.details])}"
        r = self.code
        return self.model_dump_json()
        # return details + " ".join(
        #     [str(v) for k, v in self.model_dump().items() if k != "details"]
        # )


class SnippetSource(ABC):
    @abstractmethod
    async def get_snippets(self) -> list[Snippet]: ...


class SnippetSourceGist(SnippetSource):
    gist_id: str
    comments_endpoint = "comments"
    gist_url = "https://gist.githubusercontent.com/khansgithub/{gist_id}/raw"
    gist_comments_url = "https://api.github.com/gists/{gist_id}/comments"
    markdown_factory = lambda _: Markdown(extensions=["toc", "fenced_code"])

    def __init__(self, gist_id: str) -> None:
        self.gist_id = gist_id
        super().__init__()

    def get_gist(self) -> list[Snippet]:
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
        return []

    def parse_markdown(self, raw_text: str):
        parser = ParseMarkdown(raw_text)
        try:
            md = parser.parse_markdown()
        except Exception as e:
            raise FailedGistParseError(f"Could not parse raw text: {raw_text=}") from e


class SnippetSourceFile(SnippetSource):
    path: Path

    def __init__(self, file: str | Path) -> None:
        self.path = Path(file)
        super().__init__()

    async def get_snippets(self) -> list[Snippet]:
        try:
            lines = open(self.path, "r", encoding="utf-8").read()
        except Exception as err:
            raise FailedGistFileOpenError(
                f"Could not load / read file ({self.path=})"
            ) from err

        parser = ParseMardownAsSnippets(lines)
        parser.parse_markdown()
        snippets = parser._snippets
        return snippets


class SnippetSourceRaw(SnippetSource):
    @override
    async def get_snippets(self) -> list[Snippet]:
        return [
            Snippet(
                language=SnippetLanguages.python,
                code=["..."],
                details=["first line of details", "second line of details"],
                title="foo / bar"
            ),
            Snippet(
                language=SnippetLanguages.python,
                code=[
                    r"poetry add -D black ruff pylint isort",
                    r"set FILE=config.py && isort %FILE%  && black %FILE% && ruff check %FILE% --fix  && mypy %FILE%"
                ],
                details=[],
                title="python / lint + formatting"
            ),
        ]


class ParseMardownAsSnippets(ParseMarkdown):
    _snippets: list[Snippet]

    def __init__(self, raw_text: str) -> None:
        self._snippets = []
        super().__init__(raw_text)

    @override
    def new_section(self, current_section) -> list[Never]:
        if len(current_section) != 0:
            pass
            # import ipdb; ipdb.set_trace()
        return super().new_section(current_section)

    @override
    def parse_codeblock_end(
        self, guess_code_language: bool, code_block: list[str], section_index: Index
    ) -> None:
        """ """
        section = self.get_deepest_section(self.get_root(section_index), section_index)
        print(section)
        if len(section) != 0:
            pass
            # import ipdb; ipdb.set_trace()
        snippet = Snippet(
            language=code_block[0],
            code="\n".join(code_block[1:]),
            details=self._get_headings(section_index),
            title=section_index[1],
        )

        self._snippets.append(snippet)
