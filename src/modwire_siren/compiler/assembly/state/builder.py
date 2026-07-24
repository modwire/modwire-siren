from collections.abc import Mapping
from dataclasses import dataclass, field

from pydantic import JsonValue

from ....runtime.graph import SirenApi, SirenField, SirenOperation, SirenResource, SirenRoot, SirenRoute
from ..values import FieldDraft, OperationDraft, ResourceDraft


@dataclass
class SirenBuilder:
    _root_path: str = "/"
    _root_title: str = ""
    _root_version: str = ""
    _resources: list[ResourceDraft] = field(default_factory=list)
    _operations: list[OperationDraft] = field(default_factory=list)
    _fields: list[FieldDraft] = field(default_factory=list)
    _root_operations: list[str] = field(default_factory=list)

    def set_root(self, path: str = "/", title: str = "", version: str = "") -> "SirenBuilder":
        self._root_path = path
        self._root_title = title
        self._root_version = version
        return self

    def add_resource(
        self,
        reference: str,
        name: str,
        resource_class: str,
        collection_path: str,
        entity_path: str | None = None,
        identifier: str = "id",
    ) -> "SirenBuilder":
        self._resources.append(ResourceDraft(reference, name, resource_class, collection_path, entity_path, identifier))
        return self

    def add_operation(
        self, resource: str | None, scope: str, name: str, method: str, path: str, media_type: str | None = None
    ) -> "SirenBuilder":
        self._operations.append(OperationDraft(resource, scope, name, method, path, media_type))
        return self

    def add_root_operation(self, name: str) -> "SirenBuilder":
        self._root_operations.append(name)
        return self

    def add_field(
        self, operation: str, name: str, definition: Mapping[str, JsonValue], required: bool = False
    ) -> "SirenBuilder":
        self._fields.append(FieldDraft(operation, name, definition, required))
        return self

    def build(self) -> SirenApi:
        resources = self.resource_index()
        operations = self.operation_index(resources)
        fields = self.field_index(operations)
        resource_operations = self.resource_operation_index(operations)
        return SirenApi(
            root=SirenRoot(
                route=SirenRoute(path=self._root_path),
                title=self._root_title,
                version=self._root_version,
                operations=tuple(dict.fromkeys(self._root_operations)),
            ),
            resources=tuple(
                SirenResource(
                    reference=resource.reference,
                    name=resource.name,
                    resource_class=resource.resource_class,
                    identifier=resource.identifier,
                    collection=SirenRoute(path=resource.collection_path),
                    entity=SirenRoute(path=resource.entity_path) if resource.entity_path else None,
                    collection_operations=resource_operations.get((resource.reference, "collection"), ()),
                    entity_operations=resource_operations.get((resource.reference, "entity"), ()),
                )
                for resource in resources.values()
            ),
            operations=tuple(
                SirenOperation(
                    name=operation.name,
                    resource=operation.resource,
                    scope=operation.scope,
                    method=operation.method,
                    route=SirenRoute(path=operation.path),
                    media_type=operation.media_type,
                    fields=tuple(
                        SirenField(name=item.name, definition=item.definition, required=item.required)
                        for item in fields.get(operation.name, ())
                    ),
                )
                for operation in operations.values()
            ),
        )

    def resource_index(self) -> dict[str, ResourceDraft]:
        index: dict[str, ResourceDraft] = {}
        for resource in self._resources:
            if resource.reference in index:
                raise ValueError(f"Siren resource already exists: {resource.reference}")
            index[resource.reference] = resource
        return index

    def operation_index(self, resources: Mapping[str, ResourceDraft]) -> dict[str, OperationDraft]:
        index: dict[str, OperationDraft] = {}
        for operation in self._operations:
            if operation.name in index:
                raise ValueError(f"Siren operation already exists: {operation.name}")
            if operation.scope not in {"root", "collection", "entity"}:
                raise ValueError(f"Siren operation {operation.name!r} has invalid scope {operation.scope!r}")
            if operation.scope == "root":
                if operation.resource is not None:
                    raise ValueError(f"Siren root operation {operation.name!r} cannot reference a resource")
            else:
                resource = resources.get(operation.resource)
                if resource is None:
                    raise ValueError(
                        f"Siren operation {operation.name!r} references unknown resource {operation.resource!r}"
                    )
                self.validate_operation_path(operation, resource)
            index[operation.name] = operation
        return index

    @staticmethod
    def validate_operation_path(operation: OperationDraft, resource: ResourceDraft) -> None:
        if operation.scope == "entity":
            if resource.entity_path is None:
                raise ValueError(f"Siren resource {resource.name!r} has no entity path")
            valid = operation.path == resource.entity_path or operation.path.startswith(f"{resource.entity_path}/")
        else:
            valid = operation.path == resource.collection_path or operation.path.startswith(
                f"{resource.collection_path}/"
            )
            if resource.entity_path and (
                operation.path == resource.entity_path or operation.path.startswith(f"{resource.entity_path}/")
            ):
                valid = False
        if not valid:
            raise ValueError(
                f"Siren operation {operation.name!r} path {operation.path!r} does not belong to "
                f"{operation.scope} scope of resource {resource.name!r}"
            )

    def field_index(self, operations: Mapping[str, OperationDraft]) -> dict[str, tuple[FieldDraft, ...]]:
        index: dict[str, list[FieldDraft]] = {}
        names: dict[str, set[str]] = {}
        for item in self._fields:
            if item.operation not in operations:
                raise ValueError(f"Siren field {item.name!r} references unknown operation {item.operation!r}")
            fields = index.setdefault(item.operation, [])
            operation_names = names.setdefault(item.operation, set())
            if item.name in operation_names:
                raise ValueError(f"Siren operation {item.operation!r} has duplicate field {item.name!r}")
            fields.append(item)
            operation_names.add(item.name)
        return {operation: tuple(fields) for operation, fields in index.items()}

    @staticmethod
    def resource_operation_index(operations: Mapping[str, OperationDraft]) -> dict[tuple[str, str], tuple[str, ...]]:
        index: dict[tuple[str, str], list[str]] = {}
        for operation in operations.values():
            if operation.resource is not None:
                index.setdefault((operation.resource, operation.scope), []).append(operation.name)
        return {key: tuple(names) for key, names in index.items()}
