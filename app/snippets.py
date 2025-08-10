from abc import ABC, abstractmethod
from typing import override
from models import Snippet, SnippetLanguages

class SnippetSource(ABC):
    @abstractmethod
    async def get_snippets(self) -> list[Snippet]: ...

class SnippetGist(SnippetSource): ...

class SnippetFile(SnippetSource): ...

class SnippetRaw(SnippetSource):
    @override
    async def get_snippets(self) -> list[Snippet]:
        return [
            Snippet(
                language=SnippetLanguages.python,
                code='...',
                deatils=['first line of details', 'second line of details']
            )
        ]