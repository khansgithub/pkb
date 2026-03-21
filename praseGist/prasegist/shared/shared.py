# ruff: noqa

from abc import ABC
from enum import Enum
import hashlib
import json
from pydantic import BaseModel, Field


def hashStr(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()


class BlockEnum(str, Enum):
    CODE = "code"
    TEXT = "text"


class CodeBlock(BaseModel):
    type: BlockEnum = Field(default=BlockEnum.CODE)
    lang: str
    lines: list[str] = Field(default_factory=list)
    hashes: list[str] = Field(default_factory=list)


class TextBlock(BaseModel):
    type: BlockEnum = Field(default=BlockEnum.TEXT)
    lines: list[str] = Field(default_factory=list)
    block_type: BlockEnum = Field(default=BlockEnum.TEXT, exclude=True)
    hashes: list[str] = Field(default_factory=list)
    

class Section(BaseModel):
    name: str
    level: int
    blocks: list[CodeBlock | TextBlock] = Field(default_factory=list)
    children: list["Section"] = Field(default_factory=list)


class Section1(Section):
    hashes: set[str] = Field(default_factory=set)


def block_hash(block: CodeBlock | TextBlock) -> str:
    # Using "".join([l.strip() for l in block.lines if len(l.strip()) > 0]) removes leading and trailing whitespace (including \t)
    # from each line, and skips empty (whitespace-only) lines. However, it does NOT remove whitespace inside lines.
    # If you want to remove ALL whitespace (spaces, tabs, newlines) from all lines and concatenate everything, use:
    # return hashStr("".join(l for l in block.lines).replace(" ", "").replace("\t", "").replace("\n", ""))
    # Alternatively, to remove all kinds of whitespace in a more general way:
    import re
    return hashStr(re.sub(r"\s+", "", "".join(block.lines)).lower())


# if (block.type == BlockEnum.CODE):
#     return hashStr("".join([l.strip() for l in block.lines if len(l) > 1]))
# else:
#     return hashStr("".join(filter(lambda l: len(l) > 0, block.code)))

# return hashStr("".join(filter(lambda l: len(l) > 0, block.code)))


SomeSection = Section | Section1
Snippets = list[CodeBlock | TextBlock]
