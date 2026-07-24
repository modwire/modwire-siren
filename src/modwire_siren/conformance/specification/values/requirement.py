from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SirenRequirement:
    definition: str
    member: str
    schema: Mapping[str, Any]
    required: bool
    enum_value: str | int | float | bool | None = None

    @property
    def label(self) -> str:
        if self.enum_value is None:
            return f"{self.definition}.{self.member}"
        return f"{self.definition}.{self.member}.{self.enum_value}"
