"""
Example usage of praseGist.
"""
import asyncio
import sys
from pathlib import Path

from snippets import (
    ParseMardownAsSnippets,
    SnippetSourceFile,
    SnippetSourceGist,
    SnippetSourceRaw,
)


async def example_raw() -> None:
    """Example: get snippets from the built-in raw source."""
    source = SnippetSourceRaw()
    snippets = await source.get_snippets()
    print("SnippetSourceRaw:")
    for s in snippets:
        print(f"  - {s.title}: {s.language}")


async def example_from_markdown() -> None:
    """Example: parse snippets from inline markdown."""
    markdown = """
# Python Snippets

## Formatting

```python
def hello():
    print("world")
```

## Linting

```bash
ruff check .
```
"""
    parser = ParseMardownAsSnippets(markdown)
    parser.parse_markdown()
    print("\nParseMardownAsSnippets (inline):")
    for s in parser._snippets:
        print(f"  - {s.title}: {s.language}")


async def example_from_file(filepath: Path) -> None:
    """Example: parse snippets from a markdown file."""
    source = SnippetSourceFile(filepath)
    snippets = await source.get_snippets()
    print(f"\nSnippetSourceFile ({filepath}):")
    for s in snippets:
        print(f"  - {s.title}: {s.language}")


def example_from_gist(gist_id: str) -> None:
    """Example: parse snippets from a GitHub gist."""
    import requests

    url = SnippetSourceGist.gist_url.format(gist_id=gist_id)
    res = requests.get(url)
    res.raise_for_status()
    parser = ParseMardownAsSnippets(res.text)
    parser.parse_markdown()
    print(f"\nSnippetSourceGist ({gist_id}):")
    for s in parser._snippets:
        print(f"  - {s.title}: {s.language}")


async def main() -> None:
    await example_raw()
    await example_from_markdown()

    # Uncomment to try with a file or gist:
    # await example_from_file(Path("path/to/snippets.md"))
    # example_from_gist("your-gist-id")


if __name__ == "__main__":
    asyncio.run(main())
