from collections.abc import Mapping
from typing import Literal

from pydantic import JsonValue

from sirenity.contexts.shared import BaseValue, SirenMediaType


class SirenDelegatedInput(BaseValue):
    """Describe a normalized OpenAPI input delegated to an adapter or transport.

    `kind` is the compiler-normalized structured control shape. Parameter serialization defaults
    are materialized in `style`, `explode`, and `allow_reserved`; body inputs instead carry their
    selected `media_type`.
    """

    name: str
    location: Literal["query", "header", "cookie", "body"]
    kind: Literal["array", "object", "json"]
    required: bool = False
    media_type: SirenMediaType | None = None
    style: str | None = None
    explode: bool | None = None
    allow_reserved: bool = False
    definition: Mapping[str, JsonValue] | None = None
