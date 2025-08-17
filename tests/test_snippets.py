from pathlib import Path
from unittest import IsolatedAsyncioTestCase

from app.snippets import SnippetSourceFile


class TestSnippets(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        return super().setUp()

    async def test_SnippetSourceFile(self):
        parser = SnippetSourceFile(Path(__file__).parent / "gist.md")
        snippets = await parser.get_snippets()
        for s in snippets:
            # print(json.dumps(dict(s), indent=4))
            print(dict(s))
            input("")
