import re
from abc import ABC, abstractmethod
from collections.abc import Iterable

from ..contracts.operation import OpenApiOperation
from ..contracts.resource import SirenResource
from .error import OpenApiError


class SirenResourceCatalog(ABC):
    @abstractmethod
    def operation(self, operation_id: str) -> OpenApiOperation:
        raise NotImplementedError

    @abstractmethod
    def resource(self, name: str) -> SirenResource:
        raise NotImplementedError

    @abstractmethod
    def operations(self) -> tuple[OpenApiOperation, ...]:
        raise NotImplementedError

    @abstractmethod
    def resources(self) -> tuple[SirenResource, ...]:
        raise NotImplementedError


class OpenApiCatalog(SirenResourceCatalog):
    def __init__(self, operations: tuple[OpenApiOperation, ...], resources: tuple[SirenResource, ...]):
        self._reject_duplicates("OpenAPI operationId", (item.operation_id for item in operations))
        self._reject_duplicates("Siren resource name", (item.name for item in resources))
        self._operations = {item.operation_id: item for item in operations}
        self._resources = {item.name: item for item in resources}
        self._validate_resources()

    @staticmethod
    def _reject_duplicates(label: str, values: Iterable[str]) -> None:
        seen: set[str] = set()
        duplicates: set[str] = set()
        for value in values:
            if value in seen:
                duplicates.add(value)
            seen.add(value)
        if duplicates:
            raise OpenApiError(f"Duplicate {label}: {sorted(duplicates)}")

    def operation(self, operation_id: str) -> OpenApiOperation:
        try:
            return self._operations[operation_id]
        except KeyError as error:
            raise OpenApiError(f"Unknown OpenAPI operation: {operation_id}") from error

    def operations(self) -> tuple[OpenApiOperation, ...]:
        return tuple(self._operations.values())

    def resource(self, name: str) -> SirenResource:
        try:
            return self._resources[name]
        except KeyError as error:
            raise OpenApiError(f"Unknown Siren resource: {name}") from error

    def resources(self) -> tuple[SirenResource, ...]:
        return tuple(self._resources.values())

    def _validate_resources(self) -> None:
        for resource in self._resources.values():
            placeholders = set(re.findall(r"{([^}]+)}", resource.path))
            declared = set(resource.path_parameters)
            if placeholders != declared:
                raise OpenApiError(
                    f"Resource {resource.name!r} path parameters must explicitly map "
                    f"{sorted(placeholders)}; received {sorted(declared)}"
                )
            if not resource.collection_only and resource.identifier not in resource.path_parameters.values():
                raise OpenApiError(
                    f"Resource {resource.name!r} identifier {resource.identifier!r} must be resolvable "
                    "from path-parameters"
                )
            unknown = {relation.resource for relation in resource.relations} - set(self._resources)
            if unknown:
                raise OpenApiError(f"Resource {resource.name!r} references unknown resources: {sorted(unknown)}")
            for operation_id in resource.operations:
                operation = self.operation(operation_id)
                if operation.path != resource.path and not operation.path.startswith(f"{resource.path}/"):
                    raise OpenApiError(
                        f"Operation {operation_id!r} is not owned by resource {resource.name!r}: {operation.path}"
                    )
                operation_placeholders = set(re.findall(r"{([^}]+)}", operation.path))
                extra = operation_placeholders - placeholders
                if extra:
                    raise OpenApiError(
                        f"Operation {operation_id!r} owned by resource {resource.name!r} has unmapped "
                        f"path parameters: {sorted(extra)}"
                    )
            for operation_id in resource.collection_operations:
                operation = self.operation(operation_id)
                collection_path = self._collection_path(resource.path, resource.collection_only)
                if operation.path != collection_path and not operation.path.startswith(f"{collection_path}/"):
                    raise OpenApiError(
                        f"Collection operation {operation_id!r} is not owned by resource {resource.name!r}: "
                        f"{operation.path}"
                    )
                collection_placeholders = set(re.findall(r"{([^}]+)}", collection_path))
                operation_placeholders = set(re.findall(r"{([^}]+)}", operation.path))
                extra = operation_placeholders - collection_placeholders
                if extra:
                    raise OpenApiError(
                        f"Collection operation {operation_id!r} owned by resource {resource.name!r} has unmapped "
                        f"path parameters: {sorted(extra)}"
                    )

    @staticmethod
    def _collection_path(path: str, collection_only: bool) -> str:
        if collection_only:
            return path
        parent = path.rstrip("/").rsplit("/", 1)[0]
        return parent or "/"
