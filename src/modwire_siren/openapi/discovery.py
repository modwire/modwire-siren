import re
from typing import Any

from ..contracts.resource import SirenResource
from .error import OpenApiError
from .method import OpenApiHttpMethod

_ENTITY_PATH = re.compile(r"^(?P<collection>.+)/\{(?P<parameter>[^}]+)\}$")
_PARAMETERS = re.compile(r"\{([^}]+)\}")


def discover_resources(paths: dict[str, Any]) -> tuple[SirenResource, ...]:
    resources = [_entity_resource(path, paths) for path in paths if _ENTITY_PATH.match(path)]
    entity_collections = {resource.path.rsplit("/", 1)[0] for resource in resources}
    resources.extend(
        _collection_resource(path, paths)
        for path in paths
        if _is_top_level_collection(path) and path not in entity_collections
    )
    _reject_duplicate_names(resources)
    return tuple(resources)


def _entity_resource(path: str, paths: dict[str, Any]) -> SirenResource:
    match = _ENTITY_PATH.match(path)
    assert match is not None
    collection = match.group("collection")
    parameter = match.group("parameter")
    segment = collection.rsplit("/", 1)[-1]
    name = _singular(segment)
    expected = f"{name}_id"
    if parameter != expected:
        raise OpenApiError(
            f"Siren resource path {path!r} must use {expected!r} as its entity parameter; received {parameter!r}"
        )
    entity_parameters = _path_parameters(path)
    collection_parameters = _path_parameters(collection)
    return SirenResource(
        name=name,
        path=path,
        resource_class=name.replace("_", "-"),
        identifier="id",
        path_parameters={parameter: "id"},
        relations=(),
        operations=_operations_below(paths, path, entity_parameters),
        collection_operations=_operations_below(paths, collection, collection_parameters),
    )


def _collection_resource(path: str, paths: dict[str, Any]) -> SirenResource:
    name = _singular(path.strip("/").rsplit("/", 1)[-1])
    return SirenResource(
        name=name,
        path=path,
        resource_class=name.replace("_", "-"),
        identifier="id",
        path_parameters={},
        relations=(),
        collection_operations=_operation_ids(paths[path]),
        collection_only=True,
    )


def _operations_below(paths: dict[str, Any], root: str, permitted_parameters: set[str]) -> tuple[str, ...]:
    return tuple(
        operation_id
        for path, path_item in paths.items()
        if path == root or path.startswith(f"{root}/")
        if _path_parameters(path) <= permitted_parameters
        for operation_id in _operation_ids(path_item)
    )


def _operation_ids(path_item: Any) -> tuple[str, ...]:
    if not isinstance(path_item, dict):
        return ()
    operation_ids: list[str] = []
    for method, operation in path_item.items():
        if method.lower() not in OpenApiHttpMethod or not isinstance(operation, dict):
            continue
        operation_id = operation.get("operationId")
        if not operation_id:
            raise OpenApiError(f"Siren requires operationId for {method.upper()}")
        operation_ids.append(operation_id)
    return tuple(operation_ids)


def _path_parameters(path: str) -> set[str]:
    return set(_PARAMETERS.findall(path))


def _is_top_level_collection(path: str) -> bool:
    return path.count("/") == 1 and "{" not in path and path.startswith("/")


def _singular(segment: str) -> str:
    normalized = segment.replace("-", "_")
    if not normalized.endswith("s") or len(normalized) == 1:
        raise OpenApiError(f"Siren resource collection path must be plural: {segment!r}")
    if normalized.endswith("ies"):
        return f"{normalized[:-3]}y"
    return normalized[:-1]


def _reject_duplicate_names(resources: list[SirenResource]) -> None:
    names = [resource.name for resource in resources]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise OpenApiError(f"Ambiguous Siren resources: {duplicates}")
