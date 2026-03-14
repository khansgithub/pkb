import json
from pathlib import Path

from pydantic import BaseModel, Field

from prasegist.merge.merge import OUTPUT_FILE as MERGED_GISTS
from prasegist.merge.merge import DotDict
from prasegist.shared.shared import CodeBlock, Section, SomeSection, TextBlock


OUTPUT_FILE = Path(__file__).parent / "rows.json"


class Row(BaseModel):
    title: str = Field()
    tags: list[str] = Field()
    description: str = Field()
    blocks: list[TextBlock | CodeBlock] = Field()


def load_merged_gists() -> list:
    with open(MERGED_GISTS, "r", encoding="utf-8") as f:
        return json.load(f)


def build_rows(snippets: list[SomeSection], path=[]) -> list:
    rows = []
    for snippet in snippets:
        snippet: SomeSection = DotDict(snippet)

        if not (len(snippet.blocks) == 0 and snippet.level == 1):
            rows.append(
                Row(
                    title=snippet.name,
                    tags=[snippet.name] if len(path) < 1 else path,
                    description="",
                    blocks=snippet.blocks,
                ).model_dump()
            )
        children = snippet.get("children", [])
        rows.extend(build_rows(children, [*path, snippet.name]))
    return rows


def make_rows():
    snippets = load_merged_gists()
    rows = build_rows(snippets)
    # Save rows to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
        # filtered_rows = [row for row in rows if row["tags"]]
        # filtered_out_rows = [row for row in rows if not row["tags"]]
        # json.dump(filtered_rows, f, indent=2)
        # if filtered_out_rows:
        #     print("Rows filtered out (no tags):")
        #     import pprint
        #     pprint.pprint(filtered_out_rows)


def validate_file():
    """
    Loads and parses the generated file to ensure all rows conform to the Row type.
    """
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    rows = []
    for entry in data:
        row = Row(**entry)
        rows.append(row)
    return rows

if __name__ == "__main__":
    make_rows()
    # validate_file()