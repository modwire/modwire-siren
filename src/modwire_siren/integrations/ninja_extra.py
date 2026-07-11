import inspect
from collections.abc import Awaitable, Callable, Mapping
from functools import wraps
from typing import Any, TypeVar, cast

from ..contracts.entity import SirenEmbeddedEntity, SirenEntityRequest
from ..facade import ModwireSiren

Result = Mapping[str, Any]
F = TypeVar("F", bound=Callable[..., Result | Awaitable[Result]])


class NinjaExtraSirenController:
    """Framework-light base for Ninja Extra controllers that emit Siren documents."""

    def __init__(self, siren: ModwireSiren):
        self._siren = siren

    def siren_document(
        self,
        resource_name: str,
        properties: Mapping[str, Any],
        operation_ids: tuple[str, ...],
        path_values: Mapping[str, Any],
        entities: tuple[SirenEmbeddedEntity, ...] = (),
    ) -> dict[str, Any]:
        return self._siren.document(
            SirenEntityRequest(
                resource_name=resource_name,
                properties=dict(properties),
                operation_ids=operation_ids,
                path_values=dict(path_values),
                entities=entities,
            )
        )


class SirenEntityDecorator:
    """Turn a controller method's property mapping into a Siren entity document."""

    def __init__(self, resource_name: str, *, operations: tuple[str, ...]):
        if not resource_name.strip():
            raise ValueError("Siren resource name must not be blank")
        self._resource_name = resource_name
        self._operations = operations

    def __call__(self, function: F) -> F:
        signature = inspect.signature(function)
        resource_name = self._resource_name
        operations = self._operations

        def path_values(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
            arguments = signature.bind(*args, **kwargs).arguments
            return {name: value for name, value in arguments.items() if name not in {"self", "request"}}

        if inspect.iscoroutinefunction(function):

            @wraps(function)
            async def async_wrapper(self: NinjaExtraSirenController, *args: Any, **kwargs: Any) -> dict[str, Any]:
                properties = await function(self, *args, **kwargs)
                return self.siren_document(
                    resource_name,
                    properties,
                    operations,
                    path_values((self, *args), kwargs),
                )

            return cast(F, async_wrapper)

        @wraps(function)
        def wrapper(self: NinjaExtraSirenController, *args: Any, **kwargs: Any) -> dict[str, Any]:
            properties = function(self, *args, **kwargs)
            return self.siren_document(
                resource_name,
                properties,
                operations,
                path_values((self, *args), kwargs),
            )

        return cast(F, wrapper)
