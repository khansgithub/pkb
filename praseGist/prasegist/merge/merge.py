"""
Merge comments.processed.json into gist.processed.json.

Comments are added under their tag (section) with description as subsection key.
Code blocks and misc content are converted to gist format.
"""

from dataclasses import dataclass
import json
from pathlib import Path

from prasegist.comments.parse_comments import FILEPATH as COMMENTS_FILEPATH
from prasegist.gist.parse_gist import FILEPATH as GIST_FILEPATH
from prasegist.gist.parse_gist import CodeBlock, Section, Section1, SomeSection, TextBlock, hashStr
from prasegist.shared.shared import code_block_hash, text_block_hash

GIST_PROCESSED = GIST_FILEPATH.with_suffix(".processed.json")
COMMENTS_PROCESSED = COMMENTS_FILEPATH.with_suffix(".processed.json")

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


def save_gist_processed(data: dict, path: Path | None = None) -> None:
    """Save gist.processed.json."""
    out_file = path or Path(__file__).parent / "merged_gists.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


@dataclass
class GistMap:
    section: SomeSection
    parent: SomeSection | None
def gist_map(gist: list[Section], parent: SomeSection = None) -> dict[str, GistMap]:
    r = {}
    for section in gist:
        if(hasattr(section, "children")):
            r.update(gist_map(section['children'], section))
        r[section['name']] = DotDict({
            "section": DotDict(section),
            "parent": DotDict(parent) if parent else parent
        })
    return r


def covert_hash_list_to_set(sections: list[Section1], revert=False):
    if revert:
        for section in sections:
            section.hashes = list(section.hashes)
    else:
        for section in sections:
            section.hashes = set(section.hashes)


def merge_with_section(comment: Section1, section_map: GistMap, lookup: dict[str, GistMap]):
    comment_name = _normalize_tag(comment.name)
    section = section_map.section
    for snippet in comment.snippets:
        top_level_section = section_map
        snippet: CodeBlock | TextBlock = DotDict(snippet)
        is_code = hasattr(snippet, "code")
        snippet_hash = (code_block_hash if is_code else text_block_hash)(snippet)
        
        while top_level_section.section.level > 1:
            top_level_section = lookup[top_level_section.parent.name]

        if snippet_hash in top_level_section.section.hashes:
            continue

        snippet_block = (
            CodeBlock(lang=snippet.lang, lines=snippet.code)
            if is_code
            else TextBlock(lines=snippet.text)
        )
        section.children.append(
            snippet_block.model_dump(mode="json", by_alias=True)
        )
        top_level_section.section.hashes.add(snippet_hash)


def merge2() -> dict:
    gists: list[SomeSection] = [DotDict(d) for d in load_gist_processed()]
    comments: list[Section] = [DotDict(d) for d in load_comments_processed()]

    covert_hash_list_to_set(gists)

    # merged = merge_comments_into_gist(gist_data, comments)
    ####################################################
    gist_lookup: dict[str, GistMap] = gist_map(gists)
    for comment in comments:
        comment_name = _normalize_tag(comment.name)
        section: GistMap | None = gist_lookup.get(comment_name, None)

        # new section # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
        if not section:
            # Build dict manually: comment is DotDict with comments schema, not gist
            new_section = DotDict({
                "name": comment_name,
                "level": 1,
                "snippets": [],
                "children": [dict(comment)],
                "hashes": set[str](),
            })
            gists.append(new_section)
            gist_lookup[comment_name] = new_section
            continue
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        merge_with_section(comment, section, gist_lookup)

    covert_hash_list_to_set(gists, revert=True)
    save_gist_processed(gists)
    return gists


####################################################


merge2()
