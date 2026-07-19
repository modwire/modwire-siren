from collections.abc import Mapping
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SirenRoute(Contract):
    path: str


class SirenField(Contract):
    name: str
    definition: Mapping[str, JsonValue] = Field(default_factory=dict)
    required: bool = False


class SirenOperation(Contract):
    name: str
    resource: str
    scope: Literal["collection", "entity"]
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
    route: SirenRoute
    fields: tuple[SirenField, ...] = ()


class SirenResource(Contract):
    name: str
    resource_class: str
    identifier: str = "id"
    collection: SirenRoute
    entity: SirenRoute | None = None
    collection_operations: tuple[str, ...] = ()
    entity_operations: tuple[str, ...] = ()


class SirenRoot(Contract):
    route: SirenRoute = Field(default_factory=lambda: SirenRoute(path="/"))
    title: str = ""
    version: str = ""


class SirenApi(Contract):
    root: SirenRoot = Field(default_factory=SirenRoot)
    resources: tuple[SirenResource, ...] = ()
    operations: tuple[SirenOperation, ...] = ()

    @model_validator(mode="after")
    def validate_graph(self) -> "SirenApi":
        resource_names = tuple(resource.name for resource in self.resources)
        operation_names = tuple(operation.name for operation in self.operations)
        if len(resource_names) != len(set(resource_names)):
            raise ValueError("Siren resource names must be unique")
        if len(operation_names) != len(set(operation_names)):
            raise ValueError("Siren operation names must be unique")
        unknown = {
            operation
            for resource in self.resources
            for operation in (*resource.collection_operations, *resource.entity_operations)
            if operation not in operation_names
        }
        if unknown:
            raise ValueError(f"Siren resources reference unknown operations: {sorted(unknown)}")
        resource_names_set = set(resource_names)
        unknown_resources = sorted(
            {operation.resource for operation in self.operations if operation.resource not in resource_names_set}
        )
        if unknown_resources:
            raise ValueError(f"Siren operations reference unknown resources: {unknown_resources}")
        return self


class SirenContext(Contract):
    base_url: str
    resource: str
    value: Mapping[str, JsonValue]
    path_values: Mapping[str, JsonValue] = Field(default_factory=dict)
    query: tuple[tuple[str, JsonValue], ...] = ()
    capabilities: frozenset[str] = frozenset()
