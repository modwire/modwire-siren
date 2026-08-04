from collections.abc import Mapping
from typing import Literal

from pydantic import Field, JsonValue, model_validator

from modwire_siren.contexts.shared import BaseValue, ModwireSirenError, SirenMediaType

from .relationship import SirenRelationship


class SirenResponseContext(BaseValue):
    """Supply an executed OpenAPI operation and result for operation-aware projection.

    The compiled response status, media type, and schema determine whether the result is empty,
    an object, or an array. Array responses project as collections and object responses from an
    entity's exact route project as entities. Set `representation` to `"entity"` or `"command"`
    when an object response from a collection, root, or entity-owned subcommand is ambiguous.
    """

    operation_id: str
    status: int
    result: JsonValue = None
    base_url: str
    media_type: SirenMediaType | None = None
    representation: Literal["entity", "collection", "command"] | None = None
    path_values: Mapping[str, JsonValue] = Field(default_factory=dict)
    query: tuple[tuple[str, JsonValue], ...] = ()
    capabilities: frozenset[str] = frozenset()
    item_capabilities: tuple[frozenset[str], ...] = ()
    relationships: tuple[SirenRelationship, ...] = ()

    @model_validator(mode="after")
    def validate_response(self) -> "SirenResponseContext":
        if not 100 <= self.status <= 599:
            raise ModwireSirenError("Siren response status must be between 100 and 599")
        if any(isinstance(value, (dict, list)) for _, value in self.query):
            raise ModwireSirenError("Siren query values must be scalar")
        if self.item_capabilities and (
            not isinstance(self.result, list) or len(self.item_capabilities) != len(self.result)
        ):
            raise ModwireSirenError("Siren item capabilities must align with response items")
        return self
