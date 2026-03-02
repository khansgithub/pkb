import json

from prasegist.comments.get_comments import FILEPATH
from prasegist.gist.parse_gist import CodeBlock, Section, TextBlock

# FILEPATH = FILEPATH.parent / "test_comments.json"
FILEPATH_PROCESSED = FILEPATH.with_suffix(".processed.json")


def load_comments() -> list[dict]:
    """
    Load the json file with gist comments data.
    Returns:
        list[dict]: The comments data.
    """
    try:
        with open(FILEPATH, "r", encoding="utf-8") as f:
            comments = json.load(f)
        return comments
    except (OSError, IOError) as file_err:
        print(f"Error reading from {FILEPATH}: {file_err}")
        return []
    except json.JSONDecodeError as json_err:
        print(f"Error decoding JSON from {FILEPATH}: {json_err}")
        return []


def _extract_body(comments: list[dict]) -> list[str]:
    """
    Extract the body of the comments.
    Returns:
        list[str]: The body of the comments.
    """
    return [comment["body"] for comment in comments]


class parseFunctions:
    @staticmethod
    def is_codeblock(line: str) -> bool:
        return line.strip().startswith("```")

    @staticmethod
    def is_bullet(line: str) -> bool:
        return line.strip().startswith("- ")

    @staticmethod
    def extract_bullet(line: str) -> str:
        return line.strip()[2:].strip()

    @staticmethod
    def extract_codeblock_lang(line: str) -> str:
        return line.strip().replace("`", "").strip() or ""


class Context:
    def __init__(self, line_gen=None):
        self.section: Section | None = None
        self.is_codeblock: bool = False
        self.codeblock: CodeBlock | None = None
        self.current_line: str | None = None
        self.generator = line_gen

    def _ensure_section(self, name: str = "misc"):
        if self.section is None:
            self.section = Section(name=name, level=1, snippets=[], children=[])

    def section_add(self, name: str):
        self.section = Section(name=name, level=1, snippets=[], children=[])

    def other_add(self, text: str):
        self._ensure_section()
        if self.section is not None:
            textblock = TextBlock(lines=[text])
            self.section.snippets.append(textblock)

    def start_codeblock(self, line: str):
        self._ensure_section()
        lang = parseFunctions.extract_codeblock_lang(line)
        self.codeblock = CodeBlock(lang=lang)
        if self.section is not None:
            self.section.snippets.append(self.codeblock)
        self.is_codeblock = True

    def code_add(self, line: str):
        if self.codeblock is not None:
            self.codeblock.lines.append(line.rstrip("\n"))

    def end_codeblock(self):
        self.is_codeblock = False
        self.codeblock = None

    def next(self):
        if self.generator is None:
            return None
        try:
            self.current_line = next(self.generator)
            return self.current_line
        except StopIteration:
            self.current_line = None
            return None


def parse_comment_to_section(lines: list[str]) -> Section:
    """
    Parse comment body lines into a Section.
    - First bullet (- item) becomes section name
    - Subsequent bullets become other
    - ```lang ... ``` blocks become code
    """

    def line_generator():
        for line in lines:
            yield line

    context = Context(line_generator())
    while context.next() is not None:
        parse_section(context)

    if context.section is None:
        return Section(name="misc", level=1, snippets=[], children=[])
    return context.section


def parse_section(context: Context):
    if context.is_codeblock:
        return handle_codeblock(context)
    return handle_line(context)


def handle_codeblock(context: Context):
    if parseFunctions.is_codeblock(context.current_line):
        context.end_codeblock()
        return
    context.code_add(context.current_line)


def handle_line(context: Context):
    line = context.current_line

    if parseFunctions.is_codeblock(line):
        context.start_codeblock(line)
        return

    if parseFunctions.is_bullet(line):
        bullet_text = parseFunctions.extract_bullet(line)
        if context.section is None:
            context.section_add(bullet_text)
        else:
            context.other_add(bullet_text)


def parse_comments(comments: list[str]) -> list[Section]:
    """
    Parse comment bodies into list[Section]. Each body is split into lines first.
    Returns:
        list[Section]: The parsed comments as Sections (same structure as gist).
    """
    return [
        parse_comment_to_section([line.replace("\r", "") for line in c.split("\n")])
        for c in comments
    ]


def save_comments(tree: list[Section]) -> None:
    """
    Save comments to FILEPATH_PROCESSED.
    Uses model_dump (same as gist save_gist).
    Returns:
        None
    """
    try:
        with open(FILEPATH_PROCESSED, "w", encoding="utf-8") as f:
            json.dump([s.model_dump(mode="json", by_alias=True) for s in tree], f, indent=4)
    except (OSError, IOError) as file_err:
        print(f"Error writing to {FILEPATH_PROCESSED}: {file_err}")


if __name__ == "__main__":
    comments = _extract_body(load_comments())
    tree = parse_comments(comments)
    save_comments(tree)
