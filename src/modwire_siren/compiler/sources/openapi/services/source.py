from dataclasses import dataclass
from typing import Any

from wireup import injectable

from .....runtime.graph import SirenApi
from ....assembly.services import SirenBuilder
from ....assembly.state import SirenAssembly
from ....compatibility import SirenCompatibilityFinding
from ...contracts import SirenSource
from ..state import ComponentResolver, OpenApiCompatibilityInspection, RouteCatalog
from ..state.compiler import OpenApiOperationCompiler


@injectable(as_type=SirenSource)
@dataclass(frozen=True)
class OpenApiSource(SirenSource):
    builder: SirenBuilder

    def audit(self, schema: dict[str, Any]) -> tuple[SirenCompatibilityFinding, ...]:
        paths = schema.get("paths")
        if not isinstance(paths, dict):
            return (
                SirenCompatibilityFinding(
                    "#/paths",
                    "route",
                    "OpenAPI schema requires an object-valued paths field",
                    "Use an object-valued paths field.",
                ),
            )
        return OpenApiCompatibilityInspection(
            ComponentResolver(schema.get("components", {})),
            RouteCatalog(paths),
        ).inspect()

    def load(self, schema: dict[str, Any], root_path: str) -> SirenApi:
        paths = schema.get("paths")
        if not isinstance(paths, dict):
            raise ValueError("OpenAPI schema requires an object-valued paths field")
        info = schema.get("info", {})
        assembly = SirenAssembly().set_root(
            path=root_path,
            title=str(info.get("title", "")) if isinstance(info, dict) else "",
            version=str(info.get("version", "")) if isinstance(info, dict) else "",
        )
        routes = RouteCatalog(paths)
        for resource in routes.resources():
            assembly.add_resource(
                resource.reference,
                resource.name,
                resource.resource_class,
                resource.collection_path,
                resource.entity_path,
                resource.identifier,
            )
        OpenApiOperationCompiler(assembly, routes, ComponentResolver(schema.get("components", {}))).compile()
        return self.builder.build(assembly)
