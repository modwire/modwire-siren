from collections.abc import Mapping

from pydantic import Field, JsonValue

from modwire_siren.contexts.shared import BaseValue


class SirenAdapterMatch(BaseValue):
    operation_id: str
    path_values: Mapping[str, JsonValue] = Field(default_factory=dict)
