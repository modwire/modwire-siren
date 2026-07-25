from dataclasses import dataclass, field
from typing import Any

from modwire_siren.shared import SirenActionMethod, SirenHttpMethod

from ....compatibility import SirenCompatibilityFinding
from .components import ComponentResolver
from .routes import RouteCatalog


@dataclass
class OpenApiCompatibilityInspection:
    components: ComponentResolver
    routes: RouteCatalog
    findings: list[SirenCompatibilityFinding] = field(default_factory=list)
    operation_ids: set[str] = field(default_factory=set)

    def inspect(self) -> tuple[SirenCompatibilityFinding, ...]:
        for path, path_item in self.routes.paths.items():
            self.path(path, path_item)
        return tuple(self.findings)

    def path(self, path: str, path_item: Any) -> None:
        location = self.location("paths", path)
        if not isinstance(path_item, dict):
            self.add(
                location,
                "route",
                "OpenAPI path item must be an object",
                "Use an object-valued OpenAPI path item.",
            )
            return
        if "$ref" in path_item:
            self.add(
                location,
                "component-reference",
                f"OpenAPI path item reference is unsupported: {path}",
                "Inline the path item in the Siren-facing contract.",
            )
            return
        for method, operation in path_item.items():
            self.operation(path, path_item, method, operation)

    def operation(self, path: str, path_item: dict[str, Any], method: Any, operation: Any) -> None:
        if not isinstance(method, str):
            return
        method_name = method.lower()
        if method_name == "trace":
            self.add(
                self.location("paths", path, method_name),
                "http-method",
                f"OpenAPI operation method is unsupported: TRACE {path}",
                "Use an official Siren action method: GET, POST, PUT, PATCH, or DELETE.",
            )
            return
        try:
            operation_method = SirenHttpMethod(method.upper())
        except ValueError:
            return
        if operation_method in {SirenHttpMethod.HEAD, SirenHttpMethod.OPTIONS}:
            self.add(
                self.location("paths", path, method_name),
                "http-method",
                f"OpenAPI operation method is unsupported: {method.upper()} {path}",
                "Use an official Siren action method: GET, POST, PUT, PATCH, or DELETE.",
            )
            return
        supported_methods = {SirenHttpMethod(value) for value in SirenActionMethod.values()}
        if operation_method not in supported_methods or not isinstance(operation, dict):
            return
        location = self.location("paths", path, method_name)
        name = operation.get("operationId")
        if not isinstance(name, str) or not name:
            self.add(
                location,
                "operation-id",
                f"OpenAPI operation requires operationId: {method.upper()} {path}",
                "Provide a unique operationId.",
            )
        elif name in self.operation_ids:
            self.add(
                self.location("paths", path, method_name, "operationId"),
                "operation-id",
                f"OpenAPI operationId is duplicated: {name}",
                "Use a unique operationId for every Siren action.",
            )
        else:
            self.operation_ids.add(name)
        try:
            self.routes.ownership(path)
        except ValueError as error:
            self.add(
                self.location("paths", path),
                "route",
                str(error),
                "Use an unambiguous plural collection or entity route.",
            )
        self.parameters(path_item.get("parameters", ()), self.location("paths", path, "parameters"))
        self.parameters(operation.get("parameters", ()), self.location("paths", path, method_name, "parameters"))
        self.request_body(operation, location)

    def parameters(self, parameters: Any, location: str) -> None:
        if not isinstance(parameters, (list, tuple)):
            return
        for index, parameter in enumerate(parameters):
            pointer = self.location_from(location, str(index))
            try:
                definition = self.components.parameter(parameter)
            except ValueError as error:
                self.add(pointer, "component-reference", str(error), "Use a resolvable local component reference.")
                continue
            name = definition.get("name")
            parameter_location = definition.get("in")
            if not isinstance(name, str) or not isinstance(parameter_location, str):
                self.add(
                    pointer,
                    "parameter",
                    "OpenAPI parameter requires string name and location",
                    "Provide string name and in members.",
                )
                continue
            if parameter_location == "path":
                continue
            if parameter_location != "query":
                self.add(
                    pointer,
                    "parameter-location",
                    f"OpenAPI parameter location is unsupported: {parameter_location}",
                    "Use a path parameter or an optional query parameter.",
                )
                continue
            if definition.get("required"):
                self.add(
                    pointer,
                    "required-control",
                    f"OpenAPI required query parameter is unsupported: {name}",
                    "Make the control optional in the Siren-facing contract or use a documented extension policy.",
                )
            schema = definition.get("schema")
            if not isinstance(schema, dict):
                self.add(
                    self.location_from(pointer, "schema"),
                    "field-schema",
                    f"OpenAPI parameter schema is required: {name}",
                    "Use an optional scalar field schema that maps to an official Siren field type.",
                )
                continue
            self.field(name, schema, self.location_from(pointer, "schema"))

    def request_body(self, operation: dict[str, Any], location: str) -> None:
        body_location = self.location_from(location, "requestBody")
        try:
            body = self.components.request_body(operation.get("requestBody", {}))
        except ValueError as error:
            self.add(body_location, "component-reference", str(error), "Use a resolvable local component reference.")
            return
        content = body.get("content", {}) if isinstance(body, dict) else {}
        if not content:
            return
        content_location = self.location_from(body_location, "content")
        media_location = self.location_from(content_location, "application/json")
        if not isinstance(content, dict) or not isinstance(content.get("application/json"), dict):
            self.add(
                content_location,
                "body-media-type",
                "OpenAPI request body must provide application/json",
                "Use an application/json object request body.",
            )
            return
        media = content["application/json"]
        schema = media.get("schema", {})
        schema_location = self.location_from(media_location, "schema")
        if not isinstance(schema, dict):
            self.add(
                schema_location,
                "body-schema",
                "OpenAPI request body schema is required",
                "Use an object-valued application/json schema.",
            )
            return
        try:
            definition = self.components.schema(schema)
        except ValueError as error:
            self.add(schema_location, "component-reference", str(error), "Use a resolvable local component reference.")
            return
        if definition.get("type") != "object":
            self.add(
                schema_location,
                "body-schema",
                "OpenAPI JSON request body must be an object",
                "Use an object-valued application/json schema.",
            )
            return
        properties = definition.get("properties", {})
        if not isinstance(properties, dict):
            self.add(
                self.location_from(schema_location, "properties"),
                "body-schema",
                "OpenAPI JSON request body properties must be an object",
                "Use object properties for Siren fields.",
            )
            return
        required = definition.get("required", ())
        if isinstance(required, list):
            for index, name in enumerate(required):
                self.add(
                    self.location_from(schema_location, "required", str(index)),
                    "required-control",
                    f"OpenAPI required JSON body field is unsupported: {name}",
                    "Make the control optional in the Siren-facing contract or use a documented extension policy.",
                )
        for name, value in properties.items():
            if not isinstance(name, str) or not isinstance(value, dict):
                self.add(
                    self.location_from(schema_location, "properties"),
                    "field-schema",
                    "OpenAPI JSON request body property is invalid",
                    "Use named object properties with scalar schemas.",
                )
                continue
            self.field(name, value, self.location_from(schema_location, "properties", name))

    def field(self, name: str, schema: dict[str, Any], location: str) -> None:
        try:
            definition = self.components.schema(schema)
        except ValueError as error:
            self.add(location, "component-reference", str(error), "Use a resolvable local component reference.")
            return
        unsupported = {"allOf", "anyOf", "const", "contains", "enum", "if", "items", "not", "oneOf", "prefixItems"}
        schema_type = definition.get("type")
        supported = schema_type in {"integer", "number", "boolean"}
        if schema_type == "string":
            supported = definition.get("format") in {None, "date", "date-time", "email", "time", "uri"}
        if unsupported & definition.keys() or definition.get("nullable") is True or not supported:
            self.add(
                location,
                "field-schema",
                f"OpenAPI field schema is unsupported: {name}",
                "Use an optional scalar field schema that maps to an official Siren field type.",
            )

    def add(self, location: str, category: str, detail: str, remediation: str) -> None:
        self.findings.append(SirenCompatibilityFinding(
            location=location,
            category=category,
            detail=detail,
            remediation=remediation,
        ))

    def location(self, *tokens: str) -> str:
        return "#" + "".join("/" + self.escape(token) for token in tokens)

    def location_from(self, location: str, *tokens: str) -> str:
        return location + "".join("/" + self.escape(token) for token in tokens)

    def escape(self, token: str) -> str:
        return token.replace("~", "~0").replace("/", "~1")
