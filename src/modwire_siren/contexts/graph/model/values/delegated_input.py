from collections.abc import Mapping
from typing import Literal

from pydantic import JsonValue

from modwire_siren.contexts.shared import BaseValue, SirenMediaType


class SirenDelegatedInput(BaseValue):
    name: str
    location: Literal["query", "header", "cookie", "body"]
    kind: Literal["array", "object", "json"]
    required: bool = False
    media_type: SirenMediaType | None = None
    style: str | None = None
    explode: bool | None = None
    allow_reserved: bool = False
    definition: Mapping[str, JsonValue] | None = None
