from dataclasses import dataclass
from typing import Any

from wireup import injectable

from modwire_siren.contexts.runtime.graph import SirenApi
from modwire_siren.contexts.shared import ModwireSirenError

from ...compatibility import SirenCompatibilityFinding
from ..contracts import SirenSource
from ..state import ComponentResolver, OpenApiCompatibilityInspection, RouteCatalog
from ..state.assembly import SirenAssembly
from ..state.compiler import OpenApiOperationCompiler
from .builder import SirenBuilder


@injectable(as_type=SirenSource)
@dataclass(frozen=True)
class OpenApiSource(SirenSource):
    builder: SirenBuilder

    def audit(self, schema: dict[str, Any]) -> tuple[SirenCompatibilityFinding, ...]:
        paths = schema.get("paths")
        if not isinstance(paths, dict):
            return (
                SirenCompatibilityFinding(
                    location="#/paths",
                    category="route",
                    detail="OpenAPI schema requires an object-valued paths field",
                    remediation="Use an object-valued paths field.",
                ),
            )
        return OpenApiCompatibilityInspection(
            components=ComponentResolver(components=schema.get("components", {})),
            routes=RouteCatalog(paths=paths),
        ).inspect()

    def load(self, schema: dict[str, Any], root_path: str) -> SirenApi:
        paths = schema.get("paths")
        if not isinstance(paths, dict):
            raise ModwireSirenError("OpenAPI schema requires an object-valued paths field")
        info = schema.get("info", {})
        assembly = SirenAssembly().set_root(
            path=root_path,
            title=str(info.get("title", "")) if isinstance(info, dict) else "",
            version=str(info.get("version", "")) if isinstance(info, dict) else "",
        )
        routes = RouteCatalog(paths=paths)
        for resource in routes.resources():
            assembly.add_resource(
                resource.reference,
                resource.name,
                resource.resource_class,
                resource.collection_path,
                resource.entity_path,
                resource.identifier,
            )
        OpenApiOperationCompiler(
            assembly=assembly,
            routes=routes,
            components=ComponentResolver(components=schema.get("components", {})),
        ).compile()
        return self.builder.build(assembly)
