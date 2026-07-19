from collections.abc import Sequence
from typing import Any

from .builder import SirenBuilderService
from .contracts import SirenApi, SirenOperation, SirenResource, SirenRoot
from .sources.base import SirenSource


class SirenApiService:
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
                if root != SirenRoot() and root != api.root:
                    raise ValueError("Siren sources define conflicting roots")
                root = api.root
            for resource in api.resources:
                existing = resources.get(resource.name)
                if existing is None:
                    resources[resource.name] = resource
                else:
                    resources[resource.name] = self._merge_resource(existing, resource)
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
            existing.resource_class != incoming.resource_class
            or existing.identifier != incoming.identifier
            or existing.collection != incoming.collection
            or existing.entity != incoming.entity
        ):
            raise ValueError(f"Siren sources define conflicting resource: {existing.name}")
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
            )
            for field in operation.fields:
                builder.add_field(operation.name, field.name, field.definition, field.required)
        return builder.build()
