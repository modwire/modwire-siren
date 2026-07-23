import re
from copy import deepcopy
from typing import Any

from ..builder import SirenBuilderService
from ..contracts import SirenApi
from .base import SirenSource

_ENTITY_PATH = re.compile(r"^(?P<collection>.+)/\{(?P<parameter>[^}]+)\}$")
_PARAMETERS = re.compile(r"\{([^}]+)\}")
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
        resources = self._add_resources(builder, paths)
        self._add_operations(builder, paths, resources, schema.get("components", {}))
        return builder.build()

    def _add_resources(self, builder: SirenBuilderService, paths: dict[str, Any]) -> tuple["_Resource", ...]:
        resources = tuple(self._entity_resource(path) for path in paths if _ENTITY_PATH.match(path))
        entity_collections = {resource.collection_path for resource in resources}
        resources += tuple(
            self._collection_resource(path)
            for path in paths
            if self._is_collection_path(path) and path not in entity_collections
        )
        for resource in resources:
            builder.add_resource(
                resource.name,
                resource.resource_class,
                resource.collection_path,
                resource.entity_path,
                resource.identifier,
            )
        return resources

    def _add_operations(
        self,
        builder: SirenBuilderService,
        paths: dict[str, Any],
        resources: tuple["_Resource", ...],
        components: Any,
    ) -> None:
        schemas = components.get("schemas", {}) if isinstance(components, dict) else {}
        for resource in resources:
            for path, path_item in paths.items():
                if not isinstance(path_item, dict):
                    continue
                scope = self._scope(resource, path)
                if scope is None:
                    continue
                for method, operation in path_item.items():
                    if method.lower() not in _METHODS or not isinstance(operation, dict):
                        continue
                    name = operation.get("operationId")
                    if not isinstance(name, str) or not name:
                        raise ValueError(f"OpenAPI operation requires operationId: {method.upper()} {path}")
                    builder.add_operation(resource.name, scope, name, method.upper(), path)
                    for field in self._fields(path_item, operation, schemas):
                        builder.add_field(name, field.name, field.definition, field.required)

    def _entity_resource(self, path: str) -> "_Resource":
        match = _ENTITY_PATH.match(path)
        assert match is not None
        collection_path = match.group("collection")
        name = self._singular(collection_path.rsplit("/", 1)[-1])
        parameter = match.group("parameter")
        expected = f"{name}_id"
        if parameter != expected:
            raise ValueError(f"OpenAPI entity path {path!r} requires parameter {expected!r}")
        return _Resource(name, name.replace("_", "-"), collection_path, path, "id")

    def _collection_resource(self, path: str) -> "_Resource":
        name = self._singular(path.strip("/"))
        return _Resource(name, name.replace("_", "-"), path, None, "id")

    def _scope(self, resource: "_Resource", path: str) -> str | None:
        if resource.entity_path and (
            (path == resource.entity_path or path.startswith(f"{resource.entity_path}/"))
            and self._parameters(path) == self._parameters(resource.entity_path)
        ):
            return "entity"
        if (path == resource.collection_path or path.startswith(f"{resource.collection_path}/")) and self._parameters(
            path
        ) == self._parameters(resource.collection_path):
            return "collection"
        return None

    def _fields(
        self,
        path_item: dict[str, Any],
        operation: dict[str, Any],
        schemas: dict[str, Any],
    ) -> tuple["_Field", ...]:
        parameters = (*path_item.get("parameters", ()), *operation.get("parameters", ()))
        fields = tuple(
            _Field(
                name=parameter["name"],
                definition=self._resolve(parameter.get("schema", {}), schemas),
                required=bool(parameter.get("required", False)),
            )
            for parameter in parameters
            if isinstance(parameter, dict) and parameter.get("in") == "query" and isinstance(parameter.get("name"), str)
        )
        body = operation.get("requestBody", {})
        content = body.get("content", {}) if isinstance(body, dict) else {}
        media = next(iter(content.values()), {}) if isinstance(content, dict) else {}
        definition = self._resolve(media.get("schema", {}), schemas) if isinstance(media, dict) else {}
        properties = definition.get("properties", {}) if isinstance(definition, dict) else {}
        required = set(definition.get("required", ())) if isinstance(definition, dict) else set()
        return fields + tuple(
            _Field(name=name, definition=self._resolve(value, schemas), required=name in required)
            for name, value in properties.items()
            if isinstance(name, str) and isinstance(value, dict)
        )

    def _resolve(self, definition: Any, schemas: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(definition, dict):
            return {}
        result = deepcopy(definition)
        reference = result.pop("$ref", None)
        if not isinstance(reference, str):
            return result
        name = reference.rsplit("/", 1)[-1]
        target = schemas.get(name)
        if not isinstance(target, dict):
            raise ValueError(f"OpenAPI schema reference is unknown: {reference}")
        return self._resolve(target | result, schemas)

    @staticmethod
    def _is_collection_path(path: str) -> bool:
        return path.startswith("/") and path.count("/") == 1 and "{" not in path and path.strip("/").endswith("s")

    @staticmethod
    def _singular(value: str) -> str:
        normalized = value.replace("-", "_")
        if normalized.endswith("ies"):
            return f"{normalized[:-3]}y"
        if normalized.endswith("s") and len(normalized) > 1:
            return normalized[:-1]
        raise ValueError(f"OpenAPI collection path must be plural: {value!r}")

    @staticmethod
    def _parameters(path: str) -> set[str]:
        return set(_PARAMETERS.findall(path))


class _Resource:
    def __init__(
        self,
        name: str,
        resource_class: str,
        collection_path: str,
        entity_path: str | None,
        identifier: str,
    ) -> None:
        self.name = name
        self.resource_class = resource_class
        self.collection_path = collection_path
        self.entity_path = entity_path
        self.identifier = identifier


class _Field:
    def __init__(self, name: str, definition: dict[str, Any], required: bool) -> None:
        self.name = name
        self.definition = definition
        self.required = required
