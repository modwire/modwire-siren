from collections.abc import Mapping
from typing import Any

from pydantic import Field

from sirenity.contexts.shared import BaseValue


class SirenCapability(BaseValue):
    definition: str
    schema_: Mapping[str, Any] = Field(alias="schema", serialization_alias="schema")

    @property
    def schema(self) -> Mapping[str, Any]:
        return self.schema_
