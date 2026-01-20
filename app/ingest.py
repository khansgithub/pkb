from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExtractedSnippet:
    title: str
    heading_path: str
    language: str
    code: str
    snippet_hash: str


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_snippets_from_markdown(text: str) -> list[ExtractedSnippet]:
    """
    Minimal markdown extractor:
    - tracks heading stack
    - extracts fenced code blocks (```lang ... ```)
    - assigns snippet title/path based on current headings
    """
    heading_stack: list[tuple[int, str]] = []
    snippets: list[ExtractedSnippet] = []

    in_code = False
    code_lang: str | None = None
    code_lines: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")

        if line.startswith("```"):
            if not in_code:
                in_code = True
                code_lang = (line[3:] or "plaintext").strip() or "plaintext"
                code_lines = []
            else:
                in_code = False
                code = "\n".join(code_lines).strip("\n")
                title = heading_stack[-1][1] if heading_stack else "Untitled"
                heading_path = " / ".join(h for _, h in heading_stack) or "Root"
                stable = f"{heading_path}\n{code_lang}\n{code}"
                snippets.append(
                    ExtractedSnippet(
                        title=title,
                        heading_path=heading_path,
                        language=code_lang or "plaintext",
                        code=code,
                        snippet_hash=_sha256_hex(stable),
                    )
                )
                code_lang = None
                code_lines = []
            continue

        if in_code:
            code_lines.append(line)
            continue

        m = _HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()

            # pop to parent level, then push new
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, title))

    return snippets


def load_markdown_file(path: Path) -> tuple[str, str]:
    content = path.read_text(encoding="utf-8")
    return content, _sha256_hex(content)

