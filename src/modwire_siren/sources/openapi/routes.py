import re
from dataclasses import dataclass
from typing import Any

from ...builder import SirenBuilderService

_ENTITY_PATH = re.compile(r"^(?P<collection>.+)/\{(?P<parameter>[^}]+)\}$")
_PARAMETERS = re.compile(r"\{([^}]+)\}")


@dataclass(frozen=True)
class _Resource:
    name: str
    resource_class: str
    collection_path: str
    entity_path: str | None
    identifier: str


def add_resources(builder: SirenBuilderService, paths: dict[str, Any]) -> tuple[_Resource, ...]:
    resources = tuple(_entity_resource(path) for path in paths if _ENTITY_PATH.match(path))
    entity_collections = {resource.collection_path for resource in resources}
    resources += tuple(
        _collection_resource(path) for path in paths if _is_collection_path(path) and path not in entity_collections
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


def scope(resource: _Resource, path: str) -> str | None:
    if resource.entity_path and (
        (path == resource.entity_path or path.startswith(f"{resource.entity_path}/"))
        and parameters(path) == parameters(resource.entity_path)
    ):
        return "entity"
    collection_matches = path == resource.collection_path or path.startswith(f"{resource.collection_path}/")
    if collection_matches and parameters(path) == parameters(resource.collection_path):
        return "collection"
    return None


def _entity_resource(path: str) -> _Resource:
    match = _ENTITY_PATH.match(path)
    assert match is not None
    collection_path = match.group("collection")
    name = _singular(collection_path.rsplit("/", 1)[-1])
    parameter = match.group("parameter")
    expected = f"{name}_id"
    if parameter != expected:
        raise ValueError(f"OpenAPI entity path {path!r} requires parameter {expected!r}")
    return _Resource(name, name.replace("_", "-"), collection_path, path, "id")


def _collection_resource(path: str) -> _Resource:
    name = _singular(path.strip("/"))
    return _Resource(name, name.replace("_", "-"), path, None, "id")


def _is_collection_path(path: str) -> bool:
    return path.startswith("/") and path.count("/") == 1 and "{" not in path and path.strip("/").endswith("s")


def _singular(value: str) -> str:
    normalized = value.replace("-", "_")
    if normalized.endswith("ies"):
        return f"{normalized[:-3]}y"
    if normalized.endswith("s") and len(normalized) > 1:
        return normalized[:-1]
    raise ValueError(f"OpenAPI collection path must be plural: {value!r}")


def parameters(path: str) -> set[str]:
    return set(_PARAMETERS.findall(path))
