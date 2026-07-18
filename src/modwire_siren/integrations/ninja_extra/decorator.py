import inspect
from collections.abc import Callable, Mapping
from functools import wraps
from typing import Any, TypeVar, cast

from .controller import NinjaExtraSirenController
from .response import NinjaExtraSirenResponse

F = TypeVar("F", bound=Callable[..., Any])


class SirenEntityDecorator:
    """Turn a controller method's property mapping into a Siren entity document."""

    def __init__(
        self,
        resource_name: str,
        *,
        operations: tuple[str, ...],
        as_response: bool = False,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ):
        if not resource_name.strip():
            raise ValueError("Siren resource name must not be blank")
        self._resource_name = resource_name
        self._operations = operations
        self._as_response = as_response
        self._status_code = status_code
        self._headers = dict(headers or {})

    def __call__(self, function: F) -> F:
        signature = inspect.signature(function)
        resource_name = self._resource_name
        operations = self._operations
        as_response = self._as_response
        status_code = self._status_code
        headers = self._headers

        def path_values(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
            arguments = signature.bind(*args, **kwargs).arguments
            return {name: value for name, value in arguments.items() if name not in {"self", "request"}}

        def project(
            controller: NinjaExtraSirenController,
            properties: Mapping[str, Any] | None,
            route_values: Mapping[str, Any],
        ) -> dict[str, Any] | NinjaExtraSirenResponse:
            if as_response:
                return controller.siren_response(
                    resource_name,
                    properties,
                    operation_ids=operations,
                    path_values=route_values,
                    status_code=status_code,
                    headers=headers,
                )
            if properties is None:
                raise ValueError("Siren entity documents require properties")
            return controller.siren_document(
                resource_name,
                properties,
                operations,
                route_values,
            )

        if inspect.iscoroutinefunction(function):

            @wraps(function)
            async def async_wrapper(
                self: NinjaExtraSirenController, *args: Any, **kwargs: Any
            ) -> dict[str, Any] | NinjaExtraSirenResponse:
                properties = await function(self, *args, **kwargs)
                return project(self, properties, path_values((self, *args), kwargs))

            return cast(F, async_wrapper)

        @wraps(function)
        def wrapper(
            self: NinjaExtraSirenController, *args: Any, **kwargs: Any
        ) -> dict[str, Any] | NinjaExtraSirenResponse:
            properties = function(self, *args, **kwargs)
            return project(self, properties, path_values((self, *args), kwargs))

        return cast(F, wrapper)


def siren_entity(
    *,
    resource: str,
    operations: tuple[str, ...],
    status_code: int = 200,
    headers: Mapping[str, str] | None = None,
) -> SirenEntityDecorator:
    """Turn a controller method's property mapping into a Siren response payload."""
    return SirenEntityDecorator(
        resource,
        operations=operations,
        as_response=True,
        status_code=status_code,
        headers=headers,
    )
