from typing import Any

from .resource_spec import SirenResourceSpec


class SirenResourceSpecSerializer:
    def serialize(self, resource: SirenResourceSpec) -> dict[str, Any]:
        return {
            "name": resource.name,
            "class": resource.resource_class,
            "identifier": resource.identifier,
            "path-parameters": dict(resource.path_parameters),
            "relations": {
                field: {"rel": relation.rel, "resource": relation.resource, "many": relation.many}
                for field, relation in resource.relations.items()
            },
        }
