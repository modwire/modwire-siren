from typing import Any, ClassVar

from modwire_siren.contexts.shared import (
    BaseState,
    ModwireSirenError,
    SirenActionMethod,
    SirenHttpMethod,
    SirenMediaType,
    SirenScope,
)

from ..values import Field
from .assembly import SirenAssembly
from .components import ComponentResolver
from .field_projection import OpenApiFieldProjection
from .routes import RouteCatalog


class OpenApiOperationCompiler(BaseState):
    methods: ClassVar[frozenset[SirenHttpMethod]] = frozenset(
        SirenHttpMethod(value) for value in SirenActionMethod.values()
    )
    assembly: SirenAssembly
    routes: RouteCatalog
    components: ComponentResolver
    projection: OpenApiFieldProjection

    def compile(self) -> None:
        for path, path_item in self.routes.paths.items():
            if not isinstance(path_item, dict):
                continue
            if "$ref" in path_item:
                raise ModwireSirenError(f"OpenAPI path item reference is unsupported: {path}")
            for method, operation in path_item.items():
                method_name = method.lower()
                if method_name == "trace":
                    raise ModwireSirenError(f"OpenAPI operation method is unsupported: {method.upper()} {path}")
                try:
                    operation_method = SirenHttpMethod(method.upper())
                except ValueError:
                    continue
                if operation_method in {SirenHttpMethod.HEAD, SirenHttpMethod.OPTIONS}:
                    raise ModwireSirenError(f"OpenAPI operation method is unsupported: {method.upper()} {path}")
                if operation_method not in self.methods or not isinstance(operation, dict):
                    continue
                name = operation.get("operationId")
                if not isinstance(name, str) or not name:
                    raise ModwireSirenError(f"OpenAPI operation requires operationId: {method.upper()} {path}")
                ownership = self.routes.ownership(path)
                fields, media_type = self.fields(path_item, operation)
                if ownership is None:
                    self.assembly.add_operation(
                        None, SirenScope.ROOT, name, operation_method, self.routes.public(path), media_type
                    )
                    self.assembly.add_root_operation(name)
                    for field in fields:
                        self.assembly.add_field(name, field.name, field.type, field.values, field.title, field.default)
                    continue
                resource, scope = ownership
                self.assembly.add_operation(
                    resource.reference, scope, name, operation_method, self.routes.public(path), media_type
                )
                for field in fields:
                    self.assembly.add_field(name, field.name, field.type, field.values, field.title, field.default)
                if (
                    scope == SirenScope.COLLECTION
                    and path == resource.collection_path
                    and not self.routes.parameters(path)
                    and operation_method != SirenHttpMethod.GET
                ):
                    self.assembly.add_root_operation(name)

    def fields(
        self, path_item: dict[str, Any], operation: dict[str, Any]
    ) -> tuple[tuple[Field, ...], SirenMediaType | None]:
        parameters = (*path_item.get("parameters", ()), *operation.get("parameters", ()))
        parameter_index: dict[tuple[str, str], dict[str, Any]] = {}
        for parameter in parameters:
            definition = self.components.parameter(parameter)
            name = definition.get("name")
            location = definition.get("in")
            if not isinstance(name, str) or not isinstance(location, str):
                raise ModwireSirenError("OpenAPI parameter requires string name and location")
            if location == "path":
                continue
            if location in {"header", "cookie"}:
                continue
            if location != "query":
                raise ModwireSirenError(f"OpenAPI parameter location is unsupported: {location}")
            schema = definition.get("schema")
            if not isinstance(schema, dict):
                raise ModwireSirenError(f"OpenAPI parameter schema is required: {name}")
            parameter_index[name, location] = definition
        fields: list[Field] = []
        for (name, _), definition in parameter_index.items():
            try:
                fields.append(self.projection.field(name, definition["schema"]))
            except ModwireSirenError:
                if not self.projection.delegated(definition["schema"]):
                    raise
        body = self.components.request_body(operation.get("requestBody", {}))
        content = body.get("content", {}) if isinstance(body, dict) else {}
        if content and not isinstance(content, dict):
            raise ModwireSirenError("OpenAPI request body content must be an object")
        media_name = "application/json" if isinstance(content, dict) and "application/json" in content else None
        if media_name is None and isinstance(content, dict) and len(content) == 1:
            media_name = next(iter(content))
        if content and not isinstance(media_name, str):
            raise ModwireSirenError("OpenAPI request body media types are ambiguous")
        media = content.get(media_name, {}) if isinstance(content, dict) and media_name else {}
        if content and not isinstance(media, dict):
            raise ModwireSirenError("OpenAPI request body media type is invalid")
        if media_name != "application/json":
            return tuple(fields), SirenMediaType.validate(media_name) if media_name else None
        schema = media.get("schema", {}) if isinstance(media, dict) else {}
        if content and not isinstance(schema, dict):
            raise ModwireSirenError("OpenAPI request body schema is required")
        definition = self.components.schema(schema)
        if content and definition.get("type") != "object":
            raise ModwireSirenError("OpenAPI JSON request body must be an object")
        properties = definition.get("properties", {})
        if not isinstance(properties, dict):
            raise ModwireSirenError("OpenAPI JSON request body properties must be an object")
        for name, value in properties.items():
            if not isinstance(name, str) or not isinstance(value, dict):
                raise ModwireSirenError("OpenAPI JSON request body property is invalid")
            try:
                fields.append(self.projection.field(name, value))
            except ModwireSirenError:
                if not self.projection.delegated(value):
                    raise
        return tuple(fields), SirenMediaType.validate("application/json") if content else None
