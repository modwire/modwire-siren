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

    def resource(self, name: str) -> SirenResource:
        try:
            return self._resources[name]
        except KeyError as error:
            raise OpenApiError(f"Unknown Siren resource: {name}") from error

    def _validate_resources(self) -> None:
        for resource in self._resources.values():
            placeholders = set(re.findall(r"{([^}]+)}", resource.path))
            declared = set(resource.path_parameters)
            if placeholders != declared:
                raise OpenApiError(
                    f"Resource {resource.name!r} path parameters must explicitly map "
                    f"{sorted(placeholders)}; received {sorted(declared)}"
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
