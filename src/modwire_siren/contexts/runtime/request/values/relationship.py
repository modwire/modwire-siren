from collections.abc import Mapping

from pydantic import Field, JsonValue

from modwire_siren.contexts.shared import BaseValue, SirenRelation


class SirenRelationship(BaseValue):
    """Describe a runtime relationship to another OpenAPI resource.

    A relationship projects as a navigational link by default. Set `embedded` when the related
    resource values should be included as a Siren embedded representation instead.
    """

    rel: tuple[SirenRelation, ...] = Field(min_length=1)
    resource: str
    value: Mapping[str, JsonValue] = Field(default_factory=dict)
    path_values: Mapping[str, JsonValue] = Field(default_factory=dict)
    capabilities: frozenset[str] = frozenset()
    embedded: bool = False
