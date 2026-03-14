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
    lines: list[str] = Field(default_factory=list)  # this really needs to go
    # code: list[str] = Field(default=[], repr=False, exclude=True, deprecated=True, frozen=True)


class TextBlock(BaseModel):
    type: BlockEnum = Field(default=BlockEnum.TEXT)
    lines: list[str] = Field(default_factory=list)  # this really needs to go
    block_type: BlockEnum = Field(default=BlockEnum.TEXT, exclude=True)


class Section(BaseModel):
    name: str
    level: int
    blocks: list[CodeBlock | TextBlock] = Field(default_factory=list)
    children: list["Section"] = Field(default_factory=list)


class Section1(Section):
    hashes: set[str] = Field(default_factory=set)


def block_hash(block: CodeBlock) -> str:
    return hashStr("".join([l.strip() for l in block.lines if len(l) > 1]))


# if (block.type == BlockEnum.CODE):
#     return hashStr("".join([l.strip() for l in block.lines if len(l) > 1]))
# else:
#     return hashStr("".join(filter(lambda l: len(l) > 0, block.code)))

# return hashStr("".join(filter(lambda l: len(l) > 0, block.code)))


SomeSection = Section | Section1
Snippets = list[CodeBlock | TextBlock]
