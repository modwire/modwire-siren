from typing import Any, ClassVar

from ...builder import SirenBuilderService
from .component_resolver import ComponentResolver
from .field import Field
from .route_catalog import RouteCatalog


class OperationCompiler:
    methods: ClassVar[frozenset[str]] = frozenset({"get", "post", "put", "patch", "delete", "head", "options"})

    def __init__(self, builder: SirenBuilderService, routes: RouteCatalog, components: ComponentResolver) -> None:
        self.builder = builder
        self.routes = routes
        self.components = components

    def compile(self) -> None:
        for path, path_item in self.routes.paths.items():
            if not isinstance(path_item, dict):
                continue
            for method, operation in path_item.items():
                if method.lower() not in self.methods or not isinstance(operation, dict):
                    continue
                resource, scope = self.routes.ownership(path)
                name = operation.get("operationId")
                if not isinstance(name, str) or not name:
                    raise ValueError(f"OpenAPI operation requires operationId: {method.upper()} {path}")
                self.builder.add_operation(resource.name, scope, name, method.upper(), path)
                for field in self.fields(path_item, operation):
                    self.builder.add_field(name, field.name, field.definition, field.required)

    def fields(self, path_item: dict[str, Any], operation: dict[str, Any]) -> tuple[Field, ...]:
        parameters = (*path_item.get("parameters", ()), *operation.get("parameters", ()))
        fields = []
        for parameter in parameters:
            definition = self.components.parameter(parameter)
            if definition.get("in") == "query" and isinstance(definition.get("name"), str):
                fields.append(
                    Field(
                        name=definition["name"],
                        definition=self.components.schema(definition.get("schema", {})),
                        required=bool(definition.get("required", False)),
                    )
                )
        body = self.components.request_body(operation.get("requestBody", {}))
        content = body.get("content", {}) if isinstance(body, dict) else {}
        media = next(iter(content.values()), {}) if isinstance(content, dict) else {}
        definition = self.components.schema(media.get("schema", {})) if isinstance(media, dict) else {}
        properties = definition.get("properties", {}) if isinstance(definition, dict) else {}
        required = set(definition.get("required", ())) if isinstance(definition, dict) else set()
        return tuple(fields) + tuple(
            Field(name=name, definition=self.components.schema(value), required=name in required)
            for name, value in properties.items()
            if isinstance(name, str) and isinstance(value, dict)
        )
