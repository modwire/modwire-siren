from typing import Any

from ...builder import SirenBuilderService
from ...contracts import SirenApi
from ..base import SirenSource
from .component_resolver import ComponentResolver
from .operation_compiler import OperationCompiler
from .route_catalog import RouteCatalog


class OpenApiSource(SirenSource):
    def __init__(self, root_path: str = "/") -> None:
        self.root_path = root_path

    def load(self, schema: dict[str, Any]) -> SirenApi:
        paths = schema.get("paths")
        if not isinstance(paths, dict):
            raise ValueError("OpenAPI schema requires an object-valued paths field")
        info = schema.get("info", {})
        builder = SirenBuilderService().set_root(
            path=self.root_path,
            title=str(info.get("title", "")) if isinstance(info, dict) else "",
            version=str(info.get("version", "")) if isinstance(info, dict) else "",
        )
        routes = RouteCatalog(paths)
        for resource in routes.resources():
            builder.add_resource(
                resource.name,
                resource.resource_class,
                resource.collection_path,
                resource.entity_path,
                resource.identifier,
            )
        OperationCompiler(builder, routes, ComponentResolver(schema.get("components", {}))).compile()
        return builder.build()
