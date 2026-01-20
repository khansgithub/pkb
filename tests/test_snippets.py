from pathlib import Path
from unittest import TestCase

from app.ingest import extract_snippets_from_markdown


class TestSnippets(TestCase):
    def test_extract_snippets_from_markdown(self):
        md = (Path(__file__).parent / "gist.md").read_text(encoding="utf-8")
        snippets = extract_snippets_from_markdown(md)
        self.assertGreater(len(snippets), 0)
        self.assertTrue(all(s.code.strip() for s in snippets))
