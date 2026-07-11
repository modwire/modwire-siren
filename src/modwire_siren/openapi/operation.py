from abc import ABC, abstractmethod
from typing import Any

from ..contracts.operation import OpenApiField, OpenApiOperation
from ..standards import SirenMediaType
from .error import OpenApiError
from .method import OpenApiHttpMethod
from .resolver import OpenApiSchemaResolver


class OpenApiOperationSource(ABC):
    @abstractmethod
    def read(self, paths: dict[str, Any]) -> tuple[OpenApiOperation, ...]:
        raise NotImplementedError


class OpenApiOperationReader(OpenApiOperationSource):
    def __init__(self, schemas: OpenApiSchemaResolver):
        self._schemas = schemas

    def read(self, paths: dict[str, Any]) -> tuple[OpenApiOperation, ...]:
        return tuple(
            self._operation(path, method, specification, path_item.get("parameters", ()))
            for path, path_item in paths.items()
            for method, specification in path_item.items()
            if method.lower() in OpenApiHttpMethod and isinstance(specification, dict)
        )

    def _operation(
        self,
        path: str,
        method: str,
        specification: dict[str, Any],
        path_parameters: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    ) -> OpenApiOperation:
        operation_id = specification.get("operationId")
        if not operation_id:
            raise OpenApiError(f"Siren requires operationId for {method.upper()} {path}")
        return OpenApiOperation(
            operation_id=operation_id,
            method=method.upper(),
            path=path,
            title=specification.get("summary", operation_id),
            fields=self._fields(specification, path_parameters),
        )

    def _fields(
        self,
        specification: dict[str, Any],
        path_parameters: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    ) -> tuple[OpenApiField, ...]:
        parameters = {
            (parameter.get("name"), parameter.get("in")): parameter
            for parameter in (*path_parameters, *specification.get("parameters", ()))
        }
        query = tuple(
            OpenApiField(
                name=parameter["name"],
                schema=self._schemas.resolve(parameter.get("schema", {})),
                required=parameter.get("required", False),
            )
            for parameter in parameters.values()
            if parameter.get("in") == "query"
        )
        content = specification.get("requestBody", {}).get("content", {})
        media = content.get(SirenMediaType.ACTION) or next(iter(content.values()), {})
        schema = self._schemas.resolve(media.get("schema", {}))
        required = set(schema.get("required", []))
        body = tuple(
            OpenApiField(name=name, schema=self._schemas.resolve(value), required=name in required)
            for name, value in schema.get("properties", {}).items()
        )
        return query + body
