from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal

from pydantic import JsonValue

from .contracts import SirenApi, SirenField, SirenOperation, SirenResource, SirenRoot, SirenRoute

Scope = Literal["collection", "entity"]


@dataclass
class _ResourceDraft:
    reference: str
    name: str
    resource_class: str
    collection_path: str
    entity_path: str | None
    identifier: str


@dataclass
class _OperationDraft:
    resource: str
    scope: str
    name: str
    method: str
    path: str


@dataclass
class _FieldDraft:
    operation: str
    name: str
    definition: Mapping[str, JsonValue]
    required: bool


@dataclass
class SirenBuilderService:
    _root_path: str = "/"
    _root_title: str = ""
    _root_version: str = ""
    _resources: list[_ResourceDraft] = field(default_factory=list)
    _operations: list[_OperationDraft] = field(default_factory=list)
    _fields: list[_FieldDraft] = field(default_factory=list)

    def set_root(self, path: str = "/", title: str = "", version: str = "") -> "SirenBuilderService":
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
    ) -> "SirenBuilderService":
        self._resources.append(
            _ResourceDraft(reference, name, resource_class, collection_path, entity_path, identifier)
        )
        return self

    def add_operation(
        self,
        resource: str,
        scope: Scope,
        name: str,
        method: str,
        path: str,
    ) -> "SirenBuilderService":
        self._operations.append(_OperationDraft(resource, scope, name, method, path))
        return self

    def add_field(
        self,
        operation: str,
        name: str,
        definition: Mapping[str, JsonValue],
        required: bool = False,
    ) -> "SirenBuilderService":
        self._fields.append(_FieldDraft(operation, name, definition, required))
        return self

    def build(self) -> SirenApi:
        resources = self._resource_index()
        operations = self._operation_index(resources)
        fields = self._field_index(operations)
        return SirenApi(
            root=SirenRoot(route=SirenRoute(path=self._root_path), title=self._root_title, version=self._root_version),
            resources=tuple(
                SirenResource(
                    reference=resource.reference,
                    name=resource.name,
                    resource_class=resource.resource_class,
                    identifier=resource.identifier,
                    collection=SirenRoute(path=resource.collection_path),
                    entity=SirenRoute(path=resource.entity_path) if resource.entity_path else None,
                    collection_operations=tuple(
                        operation.name
                        for operation in operations.values()
                        if operation.resource == resource.reference and operation.scope == "collection"
                    ),
                    entity_operations=tuple(
                        operation.name
                        for operation in operations.values()
                        if operation.resource == resource.reference and operation.scope == "entity"
                    ),
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
                    fields=tuple(
                        SirenField(name=item.name, definition=item.definition, required=item.required)
                        for item in fields.get(operation.name, ())
                    ),
                )
                for operation in operations.values()
            ),
        )

    def _resource_index(self) -> dict[str, _ResourceDraft]:
        index: dict[str, _ResourceDraft] = {}
        for resource in self._resources:
            if resource.reference in index:
                raise ValueError(f"Siren resource already exists: {resource.reference}")
            index[resource.reference] = resource
        return index

    def _operation_index(self, resources: Mapping[str, _ResourceDraft]) -> dict[str, _OperationDraft]:
        index: dict[str, _OperationDraft] = {}
        for operation in self._operations:
            if operation.name in index:
                raise ValueError(f"Siren operation already exists: {operation.name}")
            resource = resources.get(operation.resource)
            if resource is None:
                raise ValueError(
                    f"Siren operation {operation.name!r} references unknown resource {operation.resource!r}"
                )
            if operation.scope not in {"collection", "entity"}:
                raise ValueError(f"Siren operation {operation.name!r} has invalid scope {operation.scope!r}")
            self._validate_operation_path(operation, resource)
            index[operation.name] = operation
        return index

    @staticmethod
    def _validate_operation_path(operation: _OperationDraft, resource: _ResourceDraft) -> None:
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

    def _field_index(self, operations: Mapping[str, _OperationDraft]) -> dict[str, tuple[_FieldDraft, ...]]:
        index: dict[str, list[_FieldDraft]] = {}
        for item in self._fields:
            if item.operation not in operations:
                raise ValueError(f"Siren field {item.name!r} references unknown operation {item.operation!r}")
            fields = index.setdefault(item.operation, [])
            if item.name in {field.name for field in fields}:
                raise ValueError(f"Siren operation {item.operation!r} has duplicate field {item.name!r}")
            fields.append(item)
        return {operation: tuple(fields) for operation, fields in index.items()}
