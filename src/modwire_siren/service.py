from collections.abc import Sequence
from typing import Any

from .builder import SirenBuilderService
from .contracts import SirenApi, SirenOperation, SirenResource, SirenRoot
from .sources.base import SirenSource


class SirenApiService:
    """Build a validated Siren API graph from one or more sources."""

    def __init__(self, sources: Sequence[SirenSource]):
        self._sources = tuple(sources)

    def build(self, schema: dict[str, Any]) -> SirenApi:
        return self._build(self._merge(tuple(source.load(schema) for source in self._sources)))

    def _merge(
        self,
        apis: tuple[SirenApi, ...],
    ) -> tuple[SirenRoot, tuple[SirenResource, ...], tuple[SirenOperation, ...]]:
        root = SirenRoot()
        resources: dict[str, SirenResource] = {}
        operations: dict[str, SirenOperation] = {}
        for api in apis:
            if api.root != SirenRoot():
                if (
                    root != SirenRoot()
                    and (
                        root.route != api.root.route
                        or root.title != api.root.title
                        or root.version != api.root.version
                    )
                ):
                    raise ValueError("Siren sources define conflicting roots")
                root = api.root.model_copy(
                    update={"operations": tuple(dict.fromkeys((*root.operations, *api.root.operations)))}
                )
            for resource in api.resources:
                existing = resources.get(resource.reference)
                if existing is None:
                    resources[resource.reference] = resource
                else:
                    resources[resource.reference] = self._merge_resource(existing, resource)
            for operation in api.operations:
                existing = operations.get(operation.name)
                if existing is None:
                    operations[operation.name] = operation
                elif existing != operation:
                    raise ValueError(f"Siren sources define conflicting operation: {operation.name}")
        return root, tuple(resources.values()), tuple(operations.values())

    @staticmethod
    def _merge_resource(existing: SirenResource, incoming: SirenResource) -> SirenResource:
        if (
            existing.name != incoming.name
            or existing.reference != incoming.reference
            or existing.resource_class != incoming.resource_class
            or existing.identifier != incoming.identifier
            or existing.collection != incoming.collection
            or existing.entity != incoming.entity
        ):
            raise ValueError(f"Siren sources define conflicting resource: {existing.reference}")
        return existing.model_copy(
            update={
                "collection_operations": tuple(
                    dict.fromkeys((*existing.collection_operations, *incoming.collection_operations))
                ),
                "entity_operations": tuple(dict.fromkeys((*existing.entity_operations, *incoming.entity_operations))),
            }
        )

    def _build(self, merged: tuple[SirenRoot, tuple[SirenResource, ...], tuple[SirenOperation, ...]]) -> SirenApi:
        root, resources, operations = merged
        builder = SirenBuilderService().set_root(root.route.path, root.title, root.version)
        for resource in resources:
            builder.add_resource(
                resource.reference,
                resource.name,
                resource.resource_class,
                resource.collection.path,
                resource.entity.path if resource.entity else None,
                resource.identifier,
            )
        for operation in operations:
            builder.add_operation(
                operation.resource,
                operation.scope,
                operation.name,
                operation.method,
                operation.route.path,
                operation.media_type,
            )
            for field in operation.fields:
                builder.add_field(operation.name, field.name, field.definition, field.required)
        for operation in root.operations:
            builder.add_root_operation(operation)
        return builder.build()
