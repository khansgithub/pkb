import json
import re
from typing import Any

from langchain_ollama import OllamaLLM

from app import exceptions
from app.app_logging import logger
from app.utils import Index


class ParseMarkdown:
    raw_text: str
    _root: dict[str, list[Any]]
    _last = "_last"
    _llm = OllamaLLM(model="mistral")
    _prompt = (
        "I will give you a code block, and you will take a guess as to what language or DSL the code is in. "
        "Give me a single word answer, do not give me any further explanation at all."
        r"If you do not have 100% certainity of the language, reply with 'plaintext'."
        "I will also provide you with some text as context, to help you make a more accurate guess."
        "Use the context to take a educated guess."
        r"Respond in json, in the following format: {'prediction' : '<put your prediction here>'}"
        r"code block: \n\n{code}"
        r"context: {path}"
    )

    def __init__(self, raw_text: str) -> None:
        self.raw_text = raw_text
        self._root = {}

    def _get_headings(self, section_index: Index) -> list[str]:
        """
        grabs all the headings and their values, except for the "_" headings which are empty headings
        """
        headings = [
            k
            for k in section_index.keys()
            if isinstance(k, int) and section_index[k] != "_"
        ]

        return [section_index[h] for h in headings]

    def get_deepest_section(self, root: list, section_index, from_end=0) -> list[Any]:
        section = root
        _end_section: int = section_index.last() - from_end
        for walk_dict in range(2, _end_section + 1):
            for section_entry in section:
                if isinstance(section_entry, dict):
                    sub_section_title = section_index[walk_dict]
                    if sub_section_title in section_entry:
                        section = section_entry[sub_section_title]
                        break
        return section

    def get_root(self, section_index: Index) -> list:
        return self._root[section_index[1]]

    def _guess_codeblock_language(self, codeblock: list[str], path: str) -> str:
        code = r"\n".join(codeblock)
        language_guess = self._llm.invoke(self._prompt.format(code=code, path=path))

        lg_match = re.search("{(.*?)}", language_guess)
        if lg_match:
            lg_json: str = lg_match.group()
            try:
                lg_json = lg_json.replace("'", '"').lower()
                logger.debug("parsing: ", lg_json)
                lg_dict: dict[str, str] = json.loads(lg_json)
                language_guess = lg_dict.get("prediction", "")
            except (json.JSONDecodeError, TypeError):
                logger.error(f"Failed to guess codeblock language. {language_guess=}")
                language_guess = ""

        logger.debug(f"{language_guess=}")
        return language_guess or ""

    def guess_codeblock_language(
        self, codeblock: list[str], section_index: Index, n: int = 5
    ) -> str | None:

        # get the title of all the headings and concat it
        path = ", ".join(self._get_headings(section_index))

        freq: dict[str, int] = {}
        max_freq_count = 0
        max_freq_word = ""
        for attempt in range(n):
            guess = self._guess_codeblock_language(codeblock, path)
            if not guess:
                continue

            freq.setdefault(guess, 0)
            freq[guess] += 1
            count = freq[guess]

            if count > max_freq_count:
                max_freq_word = guess
        logger.debug(freq)
        return max_freq_word or None

    def get_codeblock_language(self, line: str, section_index: Index) -> str | None:
        """
        Parse: ```<language>
        """
        code_block_language = line[3:]
        if not code_block_language:
            logger.error(
                f"Section '{section_index[section_index.last()]}' "
                "is missing the Language for it's code block"
            )
            # code_block_language = "plaintext"
            # guess_code_language = True
            # raise Exception("Malformed code block")
        return code_block_language or None

    def parse_codeblock_end(
        self, guess_code_language: bool, code_block: list[str], section_index: Index
    ) -> None:
        """
        Updates code_block[0] with the codeblocks language, guessed by an llm
        """
        if not guess_code_language:
            return
        code_block_language = ""
        code_block_language = (
            self.guess_codeblock_language(code_block, section_index) or "plaintext"
        )

        code_block[0] = code_block_language

    def parse_markdown(self) -> dict:
        # heading / section parsing ############################################
        line_is_heading = lambda line: line[0] == "#"
        line_is_codeblock = lambda line: line.startswith("```")

        section: list[Any] = []
        section_tracker = 0
        section_index = Index()
        current_section: list[Any] = []
        ########################################################################

        # code block parsing ###################################################
        is_code_block = False
        code_block_language = ""
        code_block = []
        guess_code_language = False
        ########################################################################

        for line in self.raw_text.splitlines():
            if not line:
                continue

            if line_is_codeblock(line):
                if not is_code_block:
                    # start ```<language> of codeblock
                    is_code_block = True

                    code_block_language = (
                        self.get_codeblock_language(line, section_index) or ""
                    )

                    guess_code_language = not code_block_language

                    code_block = [code_block_language or section_index[1]]

                else:
                    # end ``` of code block
                    is_code_block = False
                    self.parse_codeblock_end(
                        guess_code_language, code_block, section_index
                    )
                    current_section.append(code_block)

            elif is_code_block:
                # currently inside a ``` codeblock
                code_block.append(line)

            elif line_is_heading(line):
                # line starts with hash
                heading_level = len(line.split(" ")[0])
                heading_title = line[heading_level + 1 :]

                if section_index.last() == 0 and heading_level != 1:
                    # if the first heading of doc is not a level 1 heading
                    raise exceptions.MissingHeadingOne(
                        "Document must start with Heading 1"
                    )

                if heading_level == 1:
                    # create a new section when we encounter a level 1 heading
                    # save the previous section to the root
                    section_index = Index()
                    current_section = []
                    self._root[heading_title] = current_section
                    section_tracker = 1
                    section_index[section_tracker] = heading_title

                elif heading_level > section_tracker:
                    # current heading is direct child of the previous
                    section = self.get_deepest_section(
                        self.get_root(section_index), section_index
                    )
                    for x in range(section_tracker + 1, heading_level):
                        # missing subsections
                        new_section: list[Any] = []
                        section.append({"_": new_section})
                        section_index[x] = "_"
                        section_tracker = x
                        section = new_section

                    current_section = []
                    section.append({heading_title: current_section})

                elif heading_level < section_tracker:
                    # current heading is not a child of the previous
                    # i.e. from heading 4 to heading 2
                    for x in range(heading_level, section_tracker + 1):
                        del section_index[x]

                    section_index.last(heading_level - 1)

                    current_section = []
                    self.get_deepest_section(
                        self.get_root(section_index), section_index
                    ).append({heading_title: current_section})

                elif heading_level == section_tracker:
                    # current heading is a sibgling of the previous
                    current_section = []
                    self.get_deepest_section(
                        self.get_root(section_index), section_index, from_end=1
                    ).append({heading_title: current_section})

                    section_index[heading_level] = heading_title

                section_index[heading_level] = heading_title
                section_index.last(heading_level)
                section_tracker = heading_level

            else:
                # any line that's not a codeblock or heading
                # TODO: need to think about how to capture other text
                #       into the snippet obj
                current_section.append(line)

        return self._root
        # with open("temp.json", "w") as f:
        #     data = self._root
        #     f.writelines(json.dumps(data, indent=4))
