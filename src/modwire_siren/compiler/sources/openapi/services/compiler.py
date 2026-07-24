from dataclasses import dataclass
from typing import Any, ClassVar

from wireup import injectable

from ....assembly.services.builder import SirenBuilder
from ..contracts import OpenApiOperationCompiler
from ..values import Field
from .components import ComponentResolver
from .routes import RouteCatalog


@injectable(as_type=OpenApiOperationCompiler)
@dataclass(frozen=True)
class OpenApiDefaultOperationCompiler(OpenApiOperationCompiler):
    methods: ClassVar[frozenset[str]] = frozenset({"get", "post", "put", "patch", "delete", "head", "options"})

    def compile(self, builder: SirenBuilder, routes: RouteCatalog, components: ComponentResolver) -> None:
        for path, path_item in routes.paths.items():
            if not isinstance(path_item, dict):
                continue
            if "$ref" in path_item:
                raise ValueError(f"OpenAPI path item reference is unsupported: {path}")
            segments = routes.segments(path)
            if (
                path.endswith("/")
                and segments
                and all(not routes.is_parameter(segment) and not routes.is_plural(segment) for segment in segments)
            ):
                continue
            for method, operation in path_item.items():
                if method.lower() == "trace":
                    raise ValueError(f"OpenAPI operation method is unsupported: TRACE {path}")
                if method.lower() not in self.methods or not isinstance(operation, dict):
                    continue
                name = operation.get("operationId")
                if not isinstance(name, str) or not name:
                    raise ValueError(f"OpenAPI operation requires operationId: {method.upper()} {path}")
                ownership = routes.ownership(path)
                if ownership is None and routes.parameters(path):
                    continue
                fields, media_type = self.fields(path_item, operation, components)
                if ownership is None:
                    builder.add_operation(None, "root", name, method.upper(), path, media_type)
                    builder.add_root_operation(name)
                    for field in fields:
                        builder.add_field(name, field.name, field.definition, field.required)
                    continue
                resource, scope = ownership
                builder.add_operation(resource.reference, scope, name, method.upper(), path, media_type)
                for field in fields:
                    builder.add_field(name, field.name, field.definition, field.required)
                if (
                    scope == "collection"
                    and path == resource.collection_path
                    and not routes.parameters(path)
                    and (method.lower() != "get" or any(field.required for field in fields))
                ):
                    builder.add_root_operation(name)

    def fields(
        self, path_item: dict[str, Any], operation: dict[str, Any], components: ComponentResolver
    ) -> tuple[tuple[Field, ...], str | None]:
        parameters = (*path_item.get("parameters", ()), *operation.get("parameters", ()))
        parameter_index: dict[tuple[str, str], dict[str, Any]] = {}
        for parameter in parameters:
            definition = components.parameter(parameter)
            name = definition.get("name")
            location = definition.get("in")
            if not isinstance(name, str) or not isinstance(location, str):
                raise ValueError("OpenAPI parameter requires string name and location")
            if location not in {"path", "query"}:
                raise ValueError(f"OpenAPI parameter location is unsupported: {location}")
            schema = definition.get("schema")
            if not isinstance(schema, dict):
                raise ValueError(f"OpenAPI parameter schema is required: {name}")
            parameter_index[name, location] = definition
        fields = tuple(
            Field(
                name=name,
                definition=components.schema(definition["schema"]),
                required=bool(definition.get("required", False)),
            )
            for (name, location), definition in parameter_index.items()
            if location == "query"
        )
        body = components.request_body(operation.get("requestBody", {}))
        content = body.get("content", {}) if isinstance(body, dict) else {}
        if content and (not isinstance(content, dict) or not isinstance(content.get("application/json"), dict)):
            raise ValueError("OpenAPI request body must provide application/json")
        media = content.get("application/json", {}) if isinstance(content, dict) else {}
        schema = media.get("schema", {}) if isinstance(media, dict) else {}
        if content and not isinstance(schema, dict):
            raise ValueError("OpenAPI request body schema is required")
        definition = components.schema(schema)
        properties = definition.get("properties", {}) if isinstance(definition, dict) else {}
        required = set(definition.get("required", ())) if isinstance(definition, dict) else set()
        return fields + tuple(
            Field(name=name, definition=components.schema(value), required=name in required)
            for name, value in properties.items()
            if isinstance(name, str) and isinstance(value, dict)
        ), "application/json" if content else None
