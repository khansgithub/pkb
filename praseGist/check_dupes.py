"""Check merged_gists.json for duplicates."""
import json
from difflib import SequenceMatcher
from pathlib import Path

SIMILARITY_THRESHOLD = 0.80

with open(Path(__file__).parent / "prasegist/merge/merged_gists.json", "r", encoding="utf-8") as f:
    data = json.load(f)


def similarity(a: str, b: str) -> float:
    """Return similarity ratio between 0 and 1."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def get_code_signature(entry, normalize=False):
    snippets = entry.get("snippets") or []
    parts = []
    for snippet in snippets:
        lines = snippet.get("code") or []
        parts.append("".join(lines))
    sig = "".join(parts)
    if normalize:
        sig = " ".join(sig.split())
    return sig


def collect_entries(items, path="", normalize=False):
    entries = []
    for i, item in enumerate(items):
        if isinstance(item, dict):
            name = item.get("name", "")
            code_sig = get_code_signature(item, normalize=normalize)
            entries.append((path, name, code_sig, item))
            children = item.get("children") or []
            entries.extend(collect_entries(children, path + "/" + str(name) + "[" + str(i) + "]", normalize))
    return entries


all_entries_norm = collect_entries(data, normalize=True)
seen_entries: list[tuple[str, str, str]] = []  # (code_sig, path, name)
duplicates_code: list[tuple[float, tuple[str, str], tuple[str, str]]] = []  # (ratio, original, dupe)

for path, name, code_sig, item in all_entries_norm:
    if not code_sig:
        continue
    matched = None
    for seen_sig, seen_path, seen_name in seen_entries:
        ratio = similarity(code_sig, seen_sig)
        if ratio >= SIMILARITY_THRESHOLD:
            matched = (ratio, (seen_path, seen_name), (path, name))
            break
    if matched:
        duplicates_code.append(matched)
    else:
        seen_entries.append((code_sig, path, name))

print(f"Duplicate pairs (>={SIMILARITY_THRESHOLD*100:.0f}% similar): {len(duplicates_code)}")
for ratio, original, dupe in duplicates_code:
    print(f"  {ratio*100:.1f}% match: {original} <-> {dupe}")
    print("------------")
