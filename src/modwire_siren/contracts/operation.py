from typing import Annotated, Any

from pydantic import Field

from .base import SirenContract


class OpenApiField(SirenContract):
    name: str
    schema_definition: Annotated[dict[str, Any], Field(validation_alias="schema")]
    required: bool


class OpenApiOperation(SirenContract):
    operation_id: str
    method: str
    path: str
    title: str
    fields: tuple[OpenApiField, ...]
