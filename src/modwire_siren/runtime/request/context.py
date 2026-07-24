from collections.abc import Mapping
from typing import Literal

from pydantic import Field, JsonValue, model_validator

from ..contracts import Contract


class SirenContext(Contract):
    """Supply runtime state used to project a Siren document.

    Use the default `"entity"` scope for one resource, `"collection"` for a list, and `"root"`
    for an API entry point. A resource is required outside root scope and is the singular name
    derived from the collection route: `"record"` for `/records`. If the same resource appears
    in multiple nested routes, `path_values` selects the route with matching parent parameters.

    | Field | Purpose |
    | --- | --- |
    | `base_url` | Public origin joined with OpenAPI paths. |
    | `scope` | `"root"`, `"collection"`, or `"entity"`. |
    | `resource` | Derived singular resource name; required outside root. |
    | `value` | Entity or collection properties and entity path parameters. |
    | `items` | Entity mappings for a collection. |
    | `path_values` | Missing path parameters, such as a parent resource ID. |
    | `query` | Ordered query pairs for self and action links. |
    | `capabilities` | Permitted OpenAPI `operationId` values. |
    """

    base_url: str
    scope: Literal["root", "collection", "entity"] = "entity"
    resource: str | None = None
    value: Mapping[str, JsonValue] = Field(default_factory=dict)
    items: tuple[Mapping[str, JsonValue], ...] = ()
    path_values: Mapping[str, JsonValue] = Field(default_factory=dict)
    query: tuple[tuple[str, JsonValue], ...] = ()
    capabilities: frozenset[str] = frozenset()

    @model_validator(mode="after")
    def validate_scope(self) -> "SirenContext":
        if self.scope == "root" and self.resource is not None:
            raise ValueError("Siren root context cannot declare a resource")
        if self.scope != "root" and self.resource is None:
            raise ValueError(f"Siren {self.scope} context requires a resource")
        if any(isinstance(value, (dict, list)) for _, value in self.query):
            raise ValueError("Siren query values must be scalar")
        return self
