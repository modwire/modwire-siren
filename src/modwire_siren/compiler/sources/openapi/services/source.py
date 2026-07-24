from dataclasses import dataclass
from typing import Any

from wireup import injectable

from .....runtime import SirenApi
from ....assembly.contracts import SirenBuilderFactory
from ...contracts import SirenSource
from ..contracts import OpenApiOperationCompiler
from ..values import ComponentResolver, RouteCatalog


@injectable(as_type=SirenSource)
@dataclass(frozen=True)
class OpenApiSource(SirenSource):
    builders: SirenBuilderFactory
    operations: OpenApiOperationCompiler

    def load(self, schema: dict[str, Any], root_path: str) -> SirenApi:
        paths = schema.get("paths")
        if not isinstance(paths, dict):
            raise ValueError("OpenAPI schema requires an object-valued paths field")
        info = schema.get("info", {})
        builder = self.builders.create().set_root(
            path=root_path,
            title=str(info.get("title", "")) if isinstance(info, dict) else "",
            version=str(info.get("version", "")) if isinstance(info, dict) else "",
        )
        routes = RouteCatalog(paths)
        for resource in routes.resources():
            builder.add_resource(
                resource.reference,
                resource.name,
                resource.resource_class,
                resource.collection_path,
                resource.entity_path,
                resource.identifier,
            )
        self.operations.compile(builder, routes, ComponentResolver(schema.get("components", {})))
        return builder.build()
