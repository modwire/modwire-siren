from collections.abc import Mapping
from typing import Any

from pydantic import Field

from sirenity.contexts.shared import BaseValue


class SirenRequirement(BaseValue):
    definition: str
    member: str
    schema_: Mapping[str, Any] = Field(alias="schema", serialization_alias="schema")
    required: bool
    document: Mapping[str, Any]
    enum_value: str | int | float | bool | None = None

    @property
    def schema(self) -> Mapping[str, Any]:
        return self.schema_

    @property
    def label(self) -> str:
        if self.enum_value is None:
            return f"{self.definition}.{self.member}"
        return f"{self.definition}.{self.member}.{self.enum_value}"
