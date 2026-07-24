from dataclasses import dataclass
from typing import Any

from wireup import injectable

from .....runtime import SirenApi
from ....assembly.state import SirenBuilder
from ...contracts import SirenSource
from ..state import ComponentResolver, RouteCatalog
from ..state.compiler import OpenApiOperationCompiler


@injectable(as_type=SirenSource)
@dataclass(frozen=True)
class OpenApiSource(SirenSource):
    def load(self, schema: dict[str, Any], root_path: str) -> SirenApi:
        paths = schema.get("paths")
        if not isinstance(paths, dict):
            raise ValueError("OpenAPI schema requires an object-valued paths field")
        info = schema.get("info", {})
        builder = SirenBuilder().set_root(
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
        OpenApiOperationCompiler(builder, routes, ComponentResolver(schema.get("components", {}))).compile()
        return builder.build()
