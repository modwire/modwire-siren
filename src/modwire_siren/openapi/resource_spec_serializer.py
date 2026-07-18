from typing import Any

from .resource_spec import SirenResourceSpec


class SirenResourceSpecSerializer:
    def serialize(self, resource: SirenResourceSpec) -> dict[str, Any]:
        extension = {
            "name": resource.name,
            "class": resource.resource_class,
            "identifier": resource.identifier,
            "path-parameters": dict(resource.path_parameters),
            "relations": {
                field: {"rel": relation.rel, "resource": relation.resource, "many": relation.many}
                for field, relation in resource.relations.items()
            },
        }
        if resource.operations:
            extension["operations"] = resource.operations
        if resource.collection_operations:
            extension["collection-operations"] = resource.collection_operations
        return extension
