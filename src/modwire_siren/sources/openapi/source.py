from typing import Any

from ...builder import SirenBuilderService
from ...contracts import SirenApi
from ..base import SirenSource
from .components import _ComponentResolver
from .routes import _Resource, add_resources, scope

_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


class OpenApiSource(SirenSource):
    def __init__(self, root_path: str = "/") -> None:
        self._root_path = root_path

    def load(self, schema: dict[str, Any]) -> SirenApi:
        paths = schema.get("paths")
        if not isinstance(paths, dict):
            raise ValueError("OpenAPI schema requires an object-valued paths field")
        info = schema.get("info", {})
        builder = SirenBuilderService().set_root(
            path=self._root_path,
            title=str(info.get("title", "")) if isinstance(info, dict) else "",
            version=str(info.get("version", "")) if isinstance(info, dict) else "",
        )
        resources = add_resources(builder, paths)
        self._add_operations(builder, paths, resources, _ComponentResolver(schema.get("components", {})))
        return builder.build()

    def _add_operations(
        self,
        builder: SirenBuilderService,
        paths: dict[str, Any],
        resources: tuple[_Resource, ...],
        resolver: _ComponentResolver,
    ) -> None:
        for resource in resources:
            for path, path_item in paths.items():
                if not isinstance(path_item, dict):
                    continue
                operation_scope = scope(resource, path)
                if operation_scope is None:
                    continue
                for method, operation in path_item.items():
                    if method.lower() not in _METHODS or not isinstance(operation, dict):
                        continue
                    name = operation.get("operationId")
                    if not isinstance(name, str) or not name:
                        raise ValueError(f"OpenAPI operation requires operationId: {method.upper()} {path}")
                    builder.add_operation(resource.name, operation_scope, name, method.upper(), path)
                    for field in self._fields(path_item, operation, resolver):
                        builder.add_field(name, field.name, field.definition, field.required)

    @staticmethod
    def _fields(
        path_item: dict[str, Any], operation: dict[str, Any], resolver: _ComponentResolver
    ) -> tuple["_Field", ...]:
        parameters = (*path_item.get("parameters", ()), *operation.get("parameters", ()))
        fields = []
        for parameter in parameters:
            definition = resolver.parameter(parameter)
            if definition.get("in") == "query" and isinstance(definition.get("name"), str):
                fields.append(
                    _Field(
                        name=definition["name"],
                        definition=resolver.schema(definition.get("schema", {})),
                        required=bool(definition.get("required", False)),
                    )
                )
        body = resolver.request_body(operation.get("requestBody", {}))
        content = body.get("content", {}) if isinstance(body, dict) else {}
        media = next(iter(content.values()), {}) if isinstance(content, dict) else {}
        definition = resolver.schema(media.get("schema", {})) if isinstance(media, dict) else {}
        properties = definition.get("properties", {}) if isinstance(definition, dict) else {}
        required = set(definition.get("required", ())) if isinstance(definition, dict) else set()
        return tuple(fields) + tuple(
            _Field(name=name, definition=resolver.schema(value), required=name in required)
            for name, value in properties.items()
            if isinstance(name, str) and isinstance(value, dict)
        )


class _Field:
    def __init__(self, name: str, definition: dict[str, Any], required: bool) -> None:
        self.name = name
        self.definition = definition
        self.required = required
