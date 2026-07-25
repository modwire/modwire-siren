from collections.abc import Mapping
from dataclasses import dataclass

from wireup import injectable

from modwire_siren.contexts.runtime.graph import (
    SirenApi,
    SirenField,
    SirenOperation,
    SirenResource,
    SirenRoot,
    SirenRoute,
)
from modwire_siren.shared import ModwireSirenError, SirenScope

from ..state import SirenAssembly
from ..values import FieldDraft, OperationDraft, ResourceDraft


@injectable
@dataclass(frozen=True)
class SirenBuilder:
    """Build a validated Siren API graph from one operation's assembly state."""

    def build(self, assembly: SirenAssembly) -> SirenApi:
        resources = self.resource_index(assembly.resources)
        operations = self.operation_index(assembly.operations, resources)
        fields = self.field_index(assembly.fields, operations)
        resource_operations = self.resource_operation_index(operations)
        return SirenApi(
            root=SirenRoot(
                route=SirenRoute(path=assembly.root_path),
                title=assembly.root_title,
                version=assembly.root_version,
                operations=tuple(dict.fromkeys(assembly.root_operations)),
            ),
            resources=tuple(
                SirenResource(
                    reference=resource.reference,
                    name=resource.name,
                    resource_class=resource.resource_class,
                    identifier=resource.identifier,
                    collection=SirenRoute(path=resource.collection_path),
                    entity=SirenRoute(path=resource.entity_path) if resource.entity_path else None,
                    collection_operations=resource_operations.get((resource.reference, SirenScope.COLLECTION), ()),
                    entity_operations=resource_operations.get((resource.reference, SirenScope.ENTITY), ()),
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
                    fields=tuple(SirenField(name=item.name, type=item.type) for item in fields.get(operation.name, ())),
                )
                for operation in operations.values()
            ),
        )

    def resource_index(self, resources: list[ResourceDraft]) -> dict[str, ResourceDraft]:
        index: dict[str, ResourceDraft] = {}
        for resource in resources:
            if resource.reference in index:
                raise ModwireSirenError(f"Siren resource already exists: {resource.reference}")
            index[resource.reference] = resource
        return index

    def operation_index(
        self, operations: list[OperationDraft], resources: Mapping[str, ResourceDraft]
    ) -> dict[str, OperationDraft]:
        index: dict[str, OperationDraft] = {}
        for operation in operations:
            if operation.name in index:
                raise ModwireSirenError(f"Siren operation already exists: {operation.name}")
            if operation.scope == SirenScope.ROOT:
                if operation.resource is not None:
                    raise ModwireSirenError(f"Siren root operation {operation.name!r} cannot reference a resource")
            else:
                resource = resources.get(operation.resource)
                if resource is None:
                    raise ModwireSirenError(
                        f"Siren operation {operation.name!r} references unknown resource {operation.resource!r}"
                    )
                self.validate_operation_path(operation, resource)
            index[operation.name] = operation
        return index

    def validate_operation_path(self, operation: OperationDraft, resource: ResourceDraft) -> None:
        if operation.scope == SirenScope.ENTITY:
            if resource.entity_path is None:
                raise ModwireSirenError(f"Siren resource {resource.name!r} has no entity path")
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
            raise ModwireSirenError(
                f"Siren operation {operation.name!r} path {operation.path!r} does not belong to "
                f"{operation.scope} scope of resource {resource.name!r}"
            )

    def field_index(
        self, fields: list[FieldDraft], operations: Mapping[str, OperationDraft]
    ) -> dict[str, tuple[FieldDraft, ...]]:
        index: dict[str, list[FieldDraft]] = {}
        names: dict[str, set[str]] = {}
        for item in fields:
            if item.operation not in operations:
                raise ModwireSirenError(f"Siren field {item.name!r} references unknown operation {item.operation!r}")
            operation_fields = index.setdefault(item.operation, [])
            operation_names = names.setdefault(item.operation, set())
            if item.name in operation_names:
                raise ModwireSirenError(f"Siren operation {item.operation!r} has duplicate field {item.name!r}")
            operation_fields.append(item)
            operation_names.add(item.name)
        return {operation: tuple(items) for operation, items in index.items()}

    def resource_operation_index(
        self, operations: Mapping[str, OperationDraft]
    ) -> dict[tuple[str, SirenScope], tuple[str, ...]]:
        index: dict[tuple[str, SirenScope], list[str]] = {}
        for operation in operations.values():
            if operation.resource is not None:
                index.setdefault((operation.resource, operation.scope), []).append(operation.name)
        return {key: tuple(names) for key, names in index.items()}
