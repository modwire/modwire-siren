from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..validation.schema import JsonSchema


@dataclass(frozen=True)
class ProfileStandard:
    schema: JsonSchema
    identifier: str
    relation: str
    entity_class: str
    revision: str

    @classmethod
    def load(cls) -> ProfileStandard:
        schema = JsonSchema("modwire_siren.profile", "schema/profile.schema.json")
        descriptor: dict[str, Any] = schema.document["x-modwire-profile"]
        return cls(
            schema=schema,
            identifier=schema.document["properties"]["profile"]["const"],
            relation=descriptor["relation"],
            entity_class=descriptor["class"],
            revision=descriptor["revision"],
        )

    @property
    def schema_id(self) -> str:
        return self.schema.document["$id"]

    @property
    def media_type(self) -> str:
        return f'application/vnd.siren+json; profile="{self.identifier}"'
