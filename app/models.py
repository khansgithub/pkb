from enum import Enum
from typing import Annotated
import pydantic


class HealthStatus(pydantic.BaseModel):
    status: str
    details: str | None = None

class SnippetLanguages(Enum):
    python = "python"
    typescript = "typescript"

class Snippet(pydantic.BaseModel):
    language: SnippetLanguages
    code: str
    deatils: Annotated[list[str], pydantic.Field(min_length=2)]