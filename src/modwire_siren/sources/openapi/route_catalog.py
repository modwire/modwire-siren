import re
from typing import Any

from .resource import Resource


class RouteCatalog:
    entity_path = re.compile(r"^(?P<collection>.+)/\{(?P<parameter>[^}]+)\}$")
    parameters = re.compile(r"\{([^}]+)\}")

    def __init__(self, paths: dict[str, Any]) -> None:
        self.paths = paths

    def resources(self) -> tuple[Resource, ...]:
        resources = tuple(self.entity_resource(path) for path in self.paths if self.entity_path.match(path))
        entity_collections = {resource.collection_path for resource in resources}
        return resources + tuple(
            self.collection_resource(path)
            for path in self.paths
            if self.collection_path(path) and path not in entity_collections
        )

    def scope(self, resource: Resource, path: str) -> str | None:
        if resource.entity_path and (
            (path == resource.entity_path or path.startswith(f"{resource.entity_path}/"))
            and self.path_parameters(path) == self.path_parameters(resource.entity_path)
        ):
            return "entity"
        collection_matches = path == resource.collection_path or path.startswith(f"{resource.collection_path}/")
        if collection_matches and self.path_parameters(path) == self.path_parameters(resource.collection_path):
            return "collection"
        return None

    def entity_resource(self, path: str) -> Resource:
        match = self.entity_path.match(path)
        assert match is not None
        collection_path = match.group("collection")
        name = self.singular(collection_path.rsplit("/", 1)[-1])
        parameter = match.group("parameter")
        expected = f"{name}_id"
        if parameter != expected:
            raise ValueError(f"OpenAPI entity path {path!r} requires parameter {expected!r}")
        return Resource(name, name.replace("_", "-"), collection_path, path, "id")

    def collection_resource(self, path: str) -> Resource:
        name = self.singular(path.strip("/"))
        return Resource(name, name.replace("_", "-"), path, None, "id")

    def collection_path(self, path: str) -> bool:
        return path.startswith("/") and path.count("/") == 1 and "{" not in path and path.strip("/").endswith("s")

    def singular(self, value: str) -> str:
        normalized = value.replace("-", "_")
        if normalized.endswith("ies"):
            return f"{normalized[:-3]}y"
        if normalized.endswith("s") and len(normalized) > 1:
            return normalized[:-1]
        raise ValueError(f"OpenAPI collection path must be plural: {value!r}")

    def path_parameters(self, path: str) -> set[str]:
        return set(self.parameters.findall(path))
