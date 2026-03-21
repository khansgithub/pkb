#!/usr/bin/env python3
"""
Export rows.json to CSV files:
  - snippets.csv: title, tags, description
    (tags = JSON array string, e.g. ["android","bash"])
  - blocks.csv: type, lang, lines, pos, snippet_idx
    (lines = JSON array of strings; pos = 1-based block index; snippet_idx = 1-based snippet index)
  String arrays (tags, lines) are serialized with json.dumps so newlines, commas,
  quotes, and backslashes inside strings are escaped and round-trip correctly.
"""
import json
import csv
from pathlib import Path

ROWS_JSON = Path(__file__).resolve().parent / "rows.json"
SNIPPETS_CSV = Path(__file__).resolve().parent / "snippets.csv"
BLOCKS_CSV = Path(__file__).resolve().parent / "blocks.csv"


def _str(val):
    """Coerce to string; None or missing -> empty string."""
    if val is None:
        return ""
    return str(val) if not isinstance(val, str) else val


def build_csv():
    with open(ROWS_JSON, encoding="utf-8") as f:
        rows = json.load(f)

    # Snippets CSV: title, tags (JSON array), description
    with open(SNIPPETS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(["title", "tags", "description"])
        for snippet in rows:
            tags = snippet.get("tags") or []
            tags_str = json.dumps(tags, ensure_ascii=False) if tags else "[]"
            w.writerow([
                _str(snippet.get("title")),
                tags_str,
                _str(snippet.get("description")),
            ])

    # Blocks CSV: type, lang, lines (JSON array), pos, snippet_idx
    with open(BLOCKS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(["type", "lang", "lines", "pos", "snippet_idx"])
        for snippet_idx, snippet in enumerate(rows, start=1):
            for pos, block in enumerate(snippet.get("blocks") or [], start=1):
                lines = block.get("lines")
                if isinstance(lines, list):
                    # JSON encodes newlines as \n, quotes as \", etc., so the
                    # CSV cell has no literal newlines; json.loads(cell) restores the array.
                    lines_str = json.dumps(lines, ensure_ascii=False)
                else:
                    lines_str = json.dumps([_str(lines)] if lines else [])
                w.writerow([
                    _str(block.get("type")),
                    _str(block.get("lang")),
                    lines_str,
                    pos,
                    snippet_idx,
                ])

    print(f"Wrote {SNIPPETS_CSV}")
    print(f"Wrote {BLOCKS_CSV}")


if __name__ == "__main__":
    build_csv()
