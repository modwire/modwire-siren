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
    reference: str
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
        resource_references = tuple(resource.reference for resource in self.resources)
        operation_names = tuple(operation.name for operation in self.operations)
        if len(resource_references) != len(set(resource_references)):
            raise ValueError("Siren resource references must be unique")
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
        resource_references_set = set(resource_references)
        unknown_resources = sorted(
            {operation.resource for operation in self.operations if operation.resource not in resource_references_set}
        )
        if unknown_resources:
            raise ValueError(f"Siren operations reference unknown resources: {unknown_resources}")
        resources = {resource.reference: resource for resource in self.resources}
        unowned = sorted(
            operation.name
            for operation in self.operations
            if operation.name
            not in (
                resources[operation.resource].collection_operations
                if operation.scope == "collection"
                else resources[operation.resource].entity_operations
            )
        )
        if unowned:
            raise ValueError(f"Siren operations are not owned by their declared resource scope: {unowned}")
        return self


class SirenContext(Contract):
    """Supply runtime state used to project a Siren document.

    Use the default `"entity"` scope for one resource, `"collection"` for a list, and `"root"`
    for an API entry point. A resource is required outside root scope and is the singular name
    derived from the collection route: `"record"` for `/records`. If the same resource appears
    in multiple nested routes, `path_values` selects the route with matching parent parameters.

    #### Collection example

    ```python
    context = SirenContext(
        base_url="https://api.example.com",
        scope="collection",
        resource="record",
        items=(
            {"id": "42", "title": "Architecture"},
            {"id": "43", "title": "Systems"},
        ),
        query=(("page", 2),),
        capabilities=frozenset({"list_records"}),
    )
    document = engine.project(context)

    assert document["links"] == [
        {"rel": ["self"], "href": "https://api.example.com/records?page=2"}
    ]
    ```

    | Field | Purpose |
    | --- | --- |
    | `base_url` | Public origin joined with OpenAPI paths, for example `https://api.example.com`. |
    | `scope` | `"root"`, `"collection"`, or `"entity"`. Root contexts have no resource. |
    | `resource` | Derived singular resource name. Required outside the root. |
    | `value` | Entity properties or collection-level properties. Also supplies entity path parameters. |
    | `items` | Tuple of entity mappings for a collection. |
    | `path_values` | Path parameters missing from `value`, such as a parent resource ID. |
    | `query` | Ordered `(name, value)` pairs added to self and action links. |
    | `capabilities` | Permitted OpenAPI `operationId` values to advertise as Siren actions. |

    #### Nested routes and queries

    For `/accounts/{account}/records/{record}`, supply the parent parameter separately:

    ```python
    context = SirenContext(
        base_url="https://api.example.com",
        resource="record",
        path_values={"account": "acme"},
        value={"record": "42", "title": "Architecture"},
    )
    ```

    Path values are percent-encoded. Query pairs retain their order and repeated keys. Query
    values must be scalar; booleans become lowercase `true` or `false`, and `None` becomes
    an empty value. The root self link receives its query pairs, while root resource links do not.
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
    def _validate_scope(self) -> "SirenContext":
        if self.scope == "root" and self.resource is not None:
            raise ValueError("Siren root context cannot declare a resource")
        if self.scope != "root" and self.resource is None:
            raise ValueError(f"Siren {self.scope} context requires a resource")
        if any(isinstance(value, (dict, list)) for _, value in self.query):
            raise ValueError("Siren query values must be scalar")
        return self
