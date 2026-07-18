from collections.abc import Mapping
from typing import Any

from ...openapi.relation_spec import SirenRelationSpec


class SirenRelationInputFactory:
    def create(self, relation: SirenRelationSpec | Mapping[str, Any]) -> SirenRelationSpec:
        if isinstance(relation, SirenRelationSpec):
            return relation
        rel = relation["rel"]
        resource = relation["resource"]
        many = relation["many"]
        if not isinstance(rel, str):
            raise ValueError("Siren relation 'rel' must be a string")
        if not isinstance(resource, str):
            raise ValueError("Siren relation 'resource' must be a string")
        if not isinstance(many, bool):
            raise ValueError("Siren relation 'many' must be a boolean")
        return SirenRelationSpec(rel=rel, resource=resource, many=many)
