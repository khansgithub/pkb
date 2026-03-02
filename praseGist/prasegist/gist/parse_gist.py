# ruff: noqa


import json
from prasegist.gist.get_gist import FILEPATH
from prasegist.shared.shared import BlockEnum, CodeBlock, Section, Section1, SomeSection, TextBlock, code_block_hash, hashStr, text_block_hash

# FILEPATH = FILEPATH.parent / "test_gist.md"
FILEPATH_PROCESSED = FILEPATH.with_suffix(".processed.json")


class Context:
    def __init__(self, line_gen=None):
        # data structures
        self.stack: list[SomeSection] = []
        self.tree: list[SomeSection] = []

        # state track
        self.is_codeblock: bool = False

        # convenience
        self.current_line = None
        self.section = None
        self.codeblock = None
        self.textblock = None

        # loop track
        self.generator = line_gen
        self.iteration = 0

    ###########
    # SECTION #
    ###########
    def section_add(self, section: SomeSection):
        if (len(self.tree)) == 0:
            # very first entry
            if section.level != 1:
                raise Exception("err")
            self.tree.append(section)
        elif len(self.stack) == 0:
            # new top level section i.e. heading 1
            self.tree.append(section)
        else:
            # new subsection
            last_section = self.stack[-1]
            last_section.children.append(section)

        # if (section.level != 1):
        #     self.stack[0].hashes.append(section.name)
        self.stack.append(section)
        self.section = section

    def section_pop(self):
        self.stack.pop()

    ########
    # CODE #
    ########
    def code_add(self, line: str):
        codeblock = self.section.snippets[-1]
        if codeblock.block_type != BlockEnum.CODE:
            raise Exception("Expect codeblock")
        codeblock.lines.append(line.rstrip().rstrip("\n"))

    def start_codeblock(self, line: str):
        lang = line.replace("`", "").strip()
        codeblock = CodeBlock(lang=lang)
        self.section.snippets.append(codeblock)
        
        self.is_codeblock = True
        self.codeblock = codeblock

    def end_codeblock(self):
        self.stack[0].hashes.add(code_block_hash(self.codeblock))
        self.stack[0].hashes.add(hashStr(self.section.name))
        
        self.is_codeblock = False
        self.codeblock = None

    #########
    # OTHER #
    #########
    def other_add(self, line: str):
        if line == "\n":
            return

        textblock = TextBlock()
        textblock.lines.append(line)
        self.section.snippets.append(textblock)
        self.textblock = textblock
        self.stack[0].hashes.add(text_block_hash(line))

    #############
    # GENERATOR #
    #############
    def next(self):
        if self.generator is None:
            return None
        try:
            self.current_line = next(self.generator)
            self.iteration += 1
            return self.current_line
        except StopIteration:
            self.current_line = None
            return None


class parseFunctions:
    def is_heading(line: str) -> bool:
        """
        1. Check if the line starts with a #.
        2. Check the line has text after the #s
        3. Make sure the heading is full of only #s (not something like #12#, only ##...)

        Args:
            line (str): line of text

        Returns:
            _bool_: line is a heading or not
        """
        return (
            line.startswith("#")
            and len((split_line := line.split(" "))) > 1
            and split_line[0].replace("#", "") == ""
        )

    def heading_level(line: str) -> int:
        i = 0
        while (line[i]) == "#":
            i += 1
        return i

    def extract_heading_details(line: str) -> tuple[int, str]:
        """
        Extracts the heading level (number of '#' at start) and the heading text.
        Returns (heading_level, heading_text).
        """
        line = line.lstrip()
        if not line.startswith("#"):
            raise Exception("Unexpected error")
        space_index = line.find(" ")
        if space_index == -1:
            # No heading text found
            raise Exception("Unexpected error")
        heading_level = space_index
        heading_text = line[space_index + 1 :].strip()
        return heading_level, heading_text

    def is_codeblock(line: str) -> bool:
        return line.startswith("```")


def load_gist() -> list[str]:
    """
    Load the gist file.
    Returns:
        list[str]: The gist text lines.
    """
    try:
        with open(FILEPATH, "r", encoding="utf-8") as f:
            gist_lines = f.readlines()
        return gist_lines
    except (OSError, IOError) as file_err:
        print(f"Error reading from {FILEPATH}: {file_err}")
        return []


def save_gist(tree: list[SomeSection]) -> None:
    """
    Save gist to FILEPATH_PROCESSED.
    Returns:
        None
    """

    def preprocess():
        out = []
        for t in tree[1:] if len(tree) > 1 else tree:
            out.append(t.model_dump(mode="json", by_alias=True))
        return out

    try:
        with open(FILEPATH_PROCESSED, "w") as f:
            # json.dump(f, tree, indent=4)
            json.dump(preprocess(), f, indent=4)
    except (OSError, IOError) as file_err:
        print(f"Error writing to {FILEPATH_PROCESSED}: {file_err}")


def parse_gist(gist_lines: list[str]) -> list[SomeSection]:
    """
    Parse the gist text lines.
    Returns:
        list[str]: The parsed gist text lines.
    """

    def line_generator():
        for line in gist_lines:
            yield line

    context = Context(line_generator())
    while context.next() is not None:
        parse_section(context)

    return context.tree


def parse_section(context: Context):
    if context.is_codeblock:
        return handle_codeblock(context)
    else:
        return handle_line(context)


def handle_codeblock(context: Context):
    is_end = parseFunctions.is_codeblock(context.current_line)
    if is_end:
        context.end_codeblock()
        return

    context.code_add(context.current_line)


def handle_line(context: Context):
    line = context.current_line

    codeblock = parseFunctions.is_codeblock(line)
    if codeblock:
        context.start_codeblock(line)
        return

    heading = parseFunctions.is_heading(line)
    if heading:
        heading_level, heading_text = parseFunctions.extract_heading_details(line)
        current_level = len(context.stack)

        if heading_level > current_level:
            pass
        elif heading_level == current_level:
            context.section_pop()
        elif heading_level < current_level:
            for _ in range(current_level - heading_level):
                context.section_pop()
            context.section_pop()

        context.section_add(
            {1: Section1}.get(heading_level, Section)(
                name=heading_text, level=heading_level
            )
        )
    else:
        context.other_add(context.current_line)
    return


if __name__ == "__main__":
    gist = load_gist()
    tree = parse_gist(gist)
    # x =json.dumps([asdict(s) for s in tree], indent=4)
    # print(json.dumps(convert_tree(tree), indent=4))
    # save_gist(convert_tree(tree))
    save_gist(tree)
