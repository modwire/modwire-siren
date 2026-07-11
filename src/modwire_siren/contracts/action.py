from typing import Annotated, Any

from pydantic import Field, field_validator

from .base import SirenContract


class SirenField(SirenContract):
    name: str
    type: str
    required: bool
    title: str
    options: tuple[dict[str, Any], ...]
    schema_definition: Annotated[dict[str, Any], Field(validation_alias="schema", serialization_alias="schema")]


class SirenAction(SirenContract):
    name: str
    href: str
    method: str
    title: str
    media_type: Annotated[str, Field(serialization_alias="type")]
    fields: tuple[SirenField, ...]

    @field_validator("method")
    @classmethod
    def normalize_method(cls, value: str) -> str:
        return value.upper()
