# ruff: noqa

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
    lang: str
    lines: list[str] = Field(default_factory=list, serialization_alias="code")
    code: list[str] = Field(default=[], repr=False, exclude=True, deprecated=True, frozen=True)
    block_type: BlockEnum = Field(default=BlockEnum.CODE, exclude=True)


class TextBlock(BaseModel):
    lines: list[str] = Field(default_factory=list, serialization_alias="text")
    text: list[str] = Field(default=[], repr=False, exclude=True, deprecated=True, frozen=True)
    block_type: BlockEnum = Field(default=BlockEnum.TEXT, exclude=True)


class Section(BaseModel):
    name: str
    level: int
    snippets: list[CodeBlock | TextBlock] = Field(default_factory=list)
    children: list["Section"] = Field(default_factory=list)


class Section1(Section):
    hashes: set[str] = Field(default_factory=set)


def code_block_hash(block: CodeBlock) -> str:
    # return hashStr("".join(filter(lambda l: len(l) > 0, block.code)))
    lines = block.lines if hasattr(block, "lines") else block.code
    return hashStr("".join([l.strip() for l in lines if len(l) > 1]))


def text_block_hash(block: TextBlock) -> str:
    lines = block.lines if hasattr(block, "lines") else block.text
    return hashStr("".join([l.strip() for l in lines if len(l) > 0]))

SomeSection = Section | Section1
Snippets = list[CodeBlock | TextBlock]