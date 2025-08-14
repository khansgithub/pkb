import json
import re
from typing import Any, Callable, cast

from langchain_ollama import OllamaLLM

from app import exceptions
from app.app_logging import logger


class ParseMarkdown:
    raw_text: str
    _root: dict[str, list[Any]]
    _last = "_last"
    _llm = OllamaLLM(model="mistral")

    def __init__(self, raw_text: str) -> None:
        self.raw_text = raw_text
        self._root = {}

    def get_deepest_section(self, root: list, section_index, from_end=0):
        section = root
        _end_section: int = section_index[self._last] - from_end
        for walk_dict in range(2, _end_section + 1):
            for section_entry in section:
                if isinstance(section_entry, dict):
                    sub_section_title = cast(str, section_index[walk_dict])
                    if sub_section_title in section_entry:
                        section = section_entry[sub_section_title]
                        break
        return section

    def get_root(self, section_index) -> list:
        return self._root[cast(str, section_index[1])]

    def _guess_codeblock_language(self, codeblock: list[str], path: str) -> str:
        code = r"\n".join(codeblock)
        template = (
            "I will give you a code block, and you will take a guess as to what language or DSL the code is in. "
            "Give me a single word answer, do not give me any further explanation at all."
            r"If you do not have 100% certainity of the language, reply with 'plaintext'."
            "I will also provide you with some text as context, to help you make a more accurate guess."
            "Use the context to take a educated guess."
            r"Respond in json, in the following format: {'prediction' : '<put your prediction here>'}"
            f"code block: \n\n{code}"
            f"context: {path}"
        )
        language_guess = self._llm.invoke(template)

        lg_match = re.search("{(.*?)}", language_guess)
        if lg_match:
            lg_json: str = lg_match.group()
            try:
                lg_json = lg_json.replace("'", '"').lower()
                logger.debug("parsing: ", lg_json)
                lg_dict: dict[str, str] = json.loads(lg_json)
                language_guess = lg_dict.get("prediction")
            except (json.JSONDecodeError, TypeError):
                logger.error(f"Failed to guess codeblock language. {language_guess=}")
                language_guess = ""

        logger.debug(f"{language_guess=}")
        return language_guess or ""

    def guess_codeblock_language(
        self, codeblock: list[str], path: str, n: int = 5
    ) -> str:
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
        return max_freq_word or ""

    def parse_markdown(self) -> dict:
        # heading / section parsing ############################################
        line_is_heading = lambda line: line[0] == "#"
        line_is_codeblock = lambda line: line.startswith("```")

        new_section_index: Callable[[], dict[str | int, str | int]] = lambda: {
            self._last: 0
        }

        section = []
        section_tracker = 0
        section_index = new_section_index()
        current_section = []
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
                # start of code block
                if not is_code_block:
                    is_code_block = True
                    code_block_language = line[3:]
                    if not code_block_language:
                        logger.error(
                            f"Section '{section_index[section_index[self._last]]}' "
                            "is missing the Language for it's code block"
                        )
                        code_block_language = "plaintext"
                        guess_code_language = True
                        # raise Exception("Malformed code block")
                    code_block = [code_block_language]

                # end of code block
                else:
                    is_code_block = False
                    if guess_code_language:
                        # grab all the headings and their values, except for the "_" headings which are empty headings
                        _headings_present = [
                            k
                            for k in section_index.keys()
                            if isinstance(k, int) and section_index[k] != "_"
                        ]

                        # get the title of all the headings and concat it
                        _path = ", ".join(
                            cast(
                                list[str], [section_index[h] for h in _headings_present]
                            )
                        )

                        code_block_language = self.guess_codeblock_language(
                            code_block, _path
                        )

                    code_block[0] = code_block_language or "plaintext"
                    current_section.append(code_block)
                    continue

            elif is_code_block:
                code_block.append(line)
                continue

            elif line_is_heading(line):
                heading_level = len(line.split(" ")[0])
                heading_title = line[heading_level + 1 :]

                if section_index[self._last] == 0 and heading_level != 1:
                    raise exceptions.MissingHeadingOne(
                        "Document must start with Heading 1"
                    )

                if heading_level == 1:
                    section_index = new_section_index()
                    current_section = []
                    self._root[heading_title] = current_section
                    section_tracker = 1
                    section_index[section_tracker] = heading_title

                elif heading_level > section_tracker:
                    # start at the relative heading 1 section
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
                    for x in range(heading_level, section_tracker + 1):
                        del section_index[x]

                    section_index[self._last] = heading_level - 1

                    current_section = []
                    section = self.get_deepest_section(
                        self.get_root(section_index), section_index
                    ).append({heading_title: current_section})

                elif heading_level == section_tracker:
                    current_section = []
                    section = self.get_deepest_section(
                        self.get_root(section_index), section_index, from_end=1
                    ).append({heading_title: current_section})

                    section_index[heading_level] = heading_title

                section_index[heading_level] = heading_title
                section_index[self._last] = heading_level
                section_tracker = heading_level

            else:
                current_section.append([line])
            # print(section_index)

        return self._root
        # with open("temp.json", "w") as f:
        #     data = self._root
        #     f.writelines(json.dumps(data, indent=4))
