from dataclasses import dataclass
from typing import Any, ClassVar

from .....runtime.vocabulary import SirenFieldType, SirenHttpMethod, SirenScope
from ....assembly.state import SirenBuilder
from ..values import Field
from .components import ComponentResolver
from .routes import RouteCatalog


@dataclass(frozen=True)
class OpenApiOperationCompiler:
    methods: ClassVar[frozenset[SirenHttpMethod]] = frozenset(
        {
            SirenHttpMethod.DELETE,
            SirenHttpMethod.GET,
            SirenHttpMethod.PATCH,
            SirenHttpMethod.POST,
            SirenHttpMethod.PUT,
        }
    )
    builder: SirenBuilder
    routes: RouteCatalog
    components: ComponentResolver

    def compile(self) -> None:
        for path, path_item in self.routes.paths.items():
            if not isinstance(path_item, dict):
                continue
            if "$ref" in path_item:
                raise ValueError(f"OpenAPI path item reference is unsupported: {path}")
            segments = self.routes.segments(path)
            if (
                path.endswith("/")
                and segments
                and all(
                    not self.routes.is_parameter(segment) and not self.routes.is_plural(segment)
                    for segment in segments
                )
            ):
                continue
            for method, operation in path_item.items():
                method_name = method.lower()
                if method_name == "trace":
                    raise ValueError(f"OpenAPI operation method is unsupported: {method.upper()} {path}")
                try:
                    operation_method = SirenHttpMethod(method.upper())
                except ValueError:
                    continue
                if operation_method in {SirenHttpMethod.HEAD, SirenHttpMethod.OPTIONS}:
                    raise ValueError(f"OpenAPI operation method is unsupported: {method.upper()} {path}")
                if operation_method not in self.methods or not isinstance(operation, dict):
                    continue
                name = operation.get("operationId")
                if not isinstance(name, str) or not name:
                    raise ValueError(f"OpenAPI operation requires operationId: {method.upper()} {path}")
                ownership = self.routes.ownership(path)
                if ownership is None and self.routes.parameters(path):
                    continue
                fields, media_type = self.fields(path_item, operation)
                if ownership is None:
                    self.builder.add_operation(None, SirenScope.ROOT, name, operation_method, path, media_type)
                    self.builder.add_root_operation(name)
                    for field in fields:
                        self.builder.add_field(name, field.name, field.type)
                    continue
                resource, scope = ownership
                self.builder.add_operation(resource.reference, scope, name, operation_method, path, media_type)
                for field in fields:
                    self.builder.add_field(name, field.name, field.type)
                if (
                    scope == SirenScope.COLLECTION
                    and path == resource.collection_path
                    and not self.routes.parameters(path)
                    and operation_method != SirenHttpMethod.GET
                ):
                    self.builder.add_root_operation(name)

    def fields(self, path_item: dict[str, Any], operation: dict[str, Any]) -> tuple[tuple[Field, ...], str | None]:
        parameters = (*path_item.get("parameters", ()), *operation.get("parameters", ()))
        parameter_index: dict[tuple[str, str], dict[str, Any]] = {}
        for parameter in parameters:
            definition = self.components.parameter(parameter)
            name = definition.get("name")
            location = definition.get("in")
            if not isinstance(name, str) or not isinstance(location, str):
                raise ValueError("OpenAPI parameter requires string name and location")
            if location == "path":
                continue
            if location != "query":
                raise ValueError(f"OpenAPI parameter location is unsupported: {location}")
            schema = definition.get("schema")
            if not isinstance(schema, dict):
                raise ValueError(f"OpenAPI parameter schema is required: {name}")
            parameter_index[name, location] = definition
        fields: list[Field] = []
        for (name, _), definition in parameter_index.items():
            if definition.get("required"):
                raise ValueError(f"OpenAPI required query parameter is unsupported: {name}")
            fields.append(Field(name=name, type=self.field_type(name, self.components.schema(definition["schema"]))))
        body = self.components.request_body(operation.get("requestBody", {}))
        content = body.get("content", {}) if isinstance(body, dict) else {}
        if content and (not isinstance(content, dict) or not isinstance(content.get("application/json"), dict)):
            raise ValueError("OpenAPI request body must provide application/json")
        media = content.get("application/json", {}) if isinstance(content, dict) else {}
        schema = media.get("schema", {}) if isinstance(media, dict) else {}
        if content and not isinstance(schema, dict):
            raise ValueError("OpenAPI request body schema is required")
        definition = self.components.schema(schema)
        if content and definition.get("type") != "object":
            raise ValueError("OpenAPI JSON request body must be an object")
        properties = definition.get("properties", {})
        if not isinstance(properties, dict):
            raise ValueError("OpenAPI JSON request body properties must be an object")
        if definition.get("required"):
            raise ValueError("OpenAPI required JSON body field is unsupported")
        for name, value in properties.items():
            if not isinstance(name, str) or not isinstance(value, dict):
                raise ValueError("OpenAPI JSON request body property is invalid")
            fields.append(Field(name=name, type=self.field_type(name, self.components.schema(value))))
        return tuple(fields), "application/json" if content else None

    def field_type(self, name: str, definition: dict[str, Any]) -> SirenFieldType:
        unsupported = {"allOf", "anyOf", "const", "contains", "enum", "if", "items", "not", "oneOf", "prefixItems"}
        if unsupported & definition.keys() or definition.get("nullable") is True:
            raise ValueError(f"OpenAPI field schema is unsupported: {name}")
        schema_type = definition.get("type")
        if schema_type == "string":
            formats = {
                "date": SirenFieldType.DATE,
                "date-time": SirenFieldType.DATETIME_LOCAL,
                "email": SirenFieldType.EMAIL,
                "time": SirenFieldType.TIME,
                "uri": SirenFieldType.URL,
            }
            field_type = formats.get(definition.get("format"), SirenFieldType.TEXT)
            if definition.get("format") is None or field_type != SirenFieldType.TEXT:
                return field_type
        if schema_type in {"integer", "number"}:
            return SirenFieldType.NUMBER
        if schema_type == "boolean":
            return SirenFieldType.CHECKBOX
        raise ValueError(f"OpenAPI field schema is unsupported: {name}")
