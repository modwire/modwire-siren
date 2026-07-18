import inspect
from collections.abc import Callable, Mapping
from functools import wraps
from typing import Any, TypeVar, cast

from .controller import NinjaExtraSirenController
from .response import EMPTY_HEADERS, NinjaExtraSirenResponse

F = TypeVar("F", bound=Callable[..., Any])


class _BaseSirenEntityDecorator:
    def __init__(self, resource_name: str, *, operations: tuple[str, ...]):
        if not resource_name.strip():
            raise ValueError("Siren resource name must not be blank")
        self._resource_name = resource_name
        self._operations = operations

    def __call__(self, function: F) -> F:
        signature = inspect.signature(function)
        decorator = self

        def path_values(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
            arguments = signature.bind(*args, **kwargs).arguments
            return {name: value for name, value in arguments.items() if name not in {"self", "request"}}

        if inspect.iscoroutinefunction(function):

            @wraps(function)
            async def async_wrapper(
                self: NinjaExtraSirenController, *args: Any, **kwargs: Any
            ) -> dict[str, Any] | NinjaExtraSirenResponse:
                properties = await function(self, *args, **kwargs)
                return decorator._project(self, properties, path_values((self, *args), kwargs))

            return cast(F, async_wrapper)

        @wraps(function)
        def wrapper(
            self: NinjaExtraSirenController, *args: Any, **kwargs: Any
        ) -> dict[str, Any] | NinjaExtraSirenResponse:
            properties = function(self, *args, **kwargs)
            return decorator._project(self, properties, path_values((self, *args), kwargs))

        return cast(F, wrapper)

    def _project(
        self,
        controller: NinjaExtraSirenController,
        properties: Any,
        route_values: Mapping[str, Any],
    ) -> dict[str, Any] | NinjaExtraSirenResponse:
        raise NotImplementedError


class SirenEntityDecorator(_BaseSirenEntityDecorator):
    """Turn a controller method's property mapping into a Siren entity document."""

    def _project(
        self,
        controller: NinjaExtraSirenController,
        properties: Any,
        route_values: Mapping[str, Any],
    ) -> dict[str, Any]:
        if properties is None:
            raise ValueError("Siren entity documents require properties")
        return controller.siren_document(
            self._resource_name,
            properties,
            self._operations,
            route_values,
        )


class _SirenEntityResponseDecorator(_BaseSirenEntityDecorator):
    def __init__(
        self,
        resource_name: str,
        *,
        operations: tuple[str, ...],
        status_code: int = 200,
        headers: Mapping[str, str] = EMPTY_HEADERS,
    ):
        super().__init__(resource_name, operations=operations)
        self._status_code = status_code
        self._headers = dict(headers)

    def _project(
        self,
        controller: NinjaExtraSirenController,
        properties: Any,
        route_values: Mapping[str, Any],
    ) -> NinjaExtraSirenResponse:
        if self._status_code == 204:
            if properties is not None:
                raise ValueError("204 Siren responses must not include a body")
            return controller.siren_responses.no_content(headers=self._headers)
        if properties is None:
            raise ValueError("Siren entity responses require properties")
        return controller.siren_response(
            self._resource_name,
            properties,
            operation_ids=self._operations,
            path_values=route_values,
            status_code=self._status_code,
            headers=self._headers,
        )


def siren_entity(
    *,
    resource: str,
    operations: tuple[str, ...],
    status_code: int = 200,
    headers: Mapping[str, str] = EMPTY_HEADERS,
) -> Callable[[F], F]:
    """Turn a controller method's property mapping into a Siren response payload."""
    return _SirenEntityResponseDecorator(
        resource,
        operations=operations,
        status_code=status_code,
        headers=headers,
    )
