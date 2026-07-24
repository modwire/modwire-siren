from collections.abc import Mapping
from dataclasses import dataclass

from pydantic import JsonValue


@dataclass(frozen=True)
class FieldDraft:
    operation: str
    name: str
    definition: Mapping[str, JsonValue]
    required: bool
