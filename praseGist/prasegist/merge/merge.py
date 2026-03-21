"""
Merge comments.processed.json into gist.processed.json.

Comments are added under their tag (section) with description as subsection key.
Code blocks and misc content are converted to gist format.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from prasegist.comments.parse_comments import FILEPATH as COMMENTS_FILEPATH
from prasegist.gist.parse_gist import FILEPATH as GIST_FILEPATH
from prasegist.gist.parse_gist import (
    CodeBlock,
    Section,
    Section1,
    SomeSection,
    TextBlock,
)
from prasegist.shared.shared import BlockEnum, block_hash
from prasegist.shared.util import find_duplicates_with_counts

GIST_PROCESSED = GIST_FILEPATH.with_suffix(".processed.json")
COMMENTS_PROCESSED = COMMENTS_FILEPATH.with_suffix(".processed.json")
OUTPUT_FILE = Path(__file__).parent / "merged_gists.json"

# Tag variations in comments -> canonical section name in gist
TAG_TO_SECTION: dict[str, str] = {
    "vscode": "vs code",
    "vs-code": "vs code",
    "node": "nodejs",
    "k8s": "k8",
    "kubernetes": "k8",
    "ts": "typescript",
    "python env": "pyenv",
}


class DotDict(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'DotDict' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(f"'DotDict' object has no attribute '{name}'")


def _normalize_tag(tag: str) -> str:
    """Map comment tag to gist section name."""
    if not tag:
        return "misc"
    lower = tag.strip().lower()
    return TAG_TO_SECTION.get(lower, tag.strip())


def load_gist_processed(path: Path | None = None) -> dict:
    """Load gist.processed.json."""
    p = path or GIST_PROCESSED
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def load_comments_processed(path: Path | None = None) -> list[dict]:
    """Load comments.processed.json."""
    p = path or COMMENTS_PROCESSED
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save_gist_processed(data: dict) -> None:
    """Save gist.processed.json."""
    out_file = OUTPUT_FILE
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


@dataclass
class GistMap:
    section: SomeSection
    parent: SomeSection | None


def gist_map(gist: list[Section], parent: SomeSection = None) -> dict[str, GistMap]:
    r = {}
    for section in gist:
        if hasattr(section, "children"):
            pass
            # r.update(gist_map(section['children'], section))
        r[section["name"]] = DotDict(
            {
                "section": DotDict(section),
                "parent": DotDict(parent) if parent else parent,
            }
        )
    return r


def covert_hash_list_to_set(sections: list[Section1], revert=False):
    if revert:
        for section in sections:
            section.hashes = list(section.hashes)
    else:
        for section in sections:
            section.hashes = set(section.hashes)

def collect_all_hashes(sections: list[Section1]) -> set:
    """
    Collect all hashes from all sections (recursively including children)
    and return as one large set.
    """
    all_hashes = set()
    def _collect(sections):
        for section in sections:
            all_hashes.update(section.hashes)
    _collect(sections)
    return all_hashes

def merge_with_section(
    comment: Section1, section_map: GistMap, lookup: dict[str, GistMap]
):
    global all_hashes
    # comment_name = _normalize_tag(comment.name)
    section = section_map.section
    for snippet in comment.blocks:
        top_level_section = section_map
        snippet: CodeBlock | TextBlock = DotDict(snippet)
        is_code = snippet.type == BlockEnum.CODE

        while top_level_section.section.level > 1:
            top_level_section = lookup[top_level_section.parent.name]

        hash_present = any([h in top_level_section.section.hashes or h in all_hashes for h in section.hashes])
        if hash_present:
            continue

        # if snippet.hash in top_level_section.section.hashes:
        #     continue
        
        # if snippet.hash in all_hashes:
        #     continue

        snippet_block = (
            CodeBlock(lang=snippet.lang, lines=snippet.lines, hashes=snippet.hashes)
            if is_code
            else TextBlock(lines=snippet.lines, hashes=snippet.hashes)
        )
        section.blocks.append(snippet_block.model_dump(mode="json"))
        top_level_section.section.hashes.update(snippet.hashes)
        all_hashes.update(snippet.hashes)


def merge2() -> dict:
    global all_hashes
    gists: list[SomeSection] = [DotDict(d) for d in load_gist_processed()]
    comments: list[Section] = [DotDict(d) for d in load_comments_processed()]

    covert_hash_list_to_set(gists)
    all_hashes = collect_all_hashes(gists)

    # merged = merge_comments_into_gist(gist_data, comments)
    ####################################################
    gist_lookup: dict[str, GistMap] = gist_map(gists)
    for comment in comments:
        comment_name = _normalize_tag(comment.name)
        section: GistMap | None = gist_lookup.get(comment_name, None)

        # new section # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        if not section:

            # Filter out all codeblocks and textblocks whose hash is present in all_hashes, in comment.
            filtered_blocks = []
            for snippet in comment.blocks:
                snippet_hash = block_hash(DotDict(snippet))
                if snippet_hash not in all_hashes:
                    all_hashes.add(snippet_hash)
                    filtered_blocks.append(snippet)
            comment.blocks = filtered_blocks
            # Build dict manually: comment is DotDict with comments schema, not gist

            new_section = DotDict(
                Section1(
                    name=comment_name,
                    level=1,
                    blocks=[],
                    children=[dict(comment)],
                    hashes=set(),
                ).model_dump()
            )
            gists.append(new_section)
            gist_lookup[comment_name] = GistMap(
                section=new_section,
                parent=None,
            )
            continue
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        merge_with_section(comment, section, gist_lookup)

    covert_hash_list_to_set(gists, revert=True)
    save_gist_processed(gists)

    all_hashes2 = []
    for gist in gists:
        all_hashes2.extend(gist.hashes)
    x = find_duplicates_with_counts(all_hashes2)
    print(x)
    return gists


####################################################

if __name__ == "__main__":
    merge2()
