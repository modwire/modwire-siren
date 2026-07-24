from collections.abc import Mapping

from pydantic import Field, JsonValue

from .contract import Contract


class SirenField(Contract):
    name: str
    definition: Mapping[str, JsonValue] = Field(default_factory=dict)
    required: bool = False
