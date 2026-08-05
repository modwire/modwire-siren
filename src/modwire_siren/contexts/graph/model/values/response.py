from collections.abc import Mapping
from typing import Literal

from pydantic import JsonValue

from modwire_siren.contexts.shared import BaseValue, SirenMediaType


class SirenResponse(BaseValue):
    status: str
    media_type: SirenMediaType | None = None
    shape: Literal["object", "array", "empty"]
    definition: Mapping[str, JsonValue] | None = None
