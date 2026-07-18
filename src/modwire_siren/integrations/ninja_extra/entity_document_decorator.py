import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from .controller import NinjaExtraSirenController
from .route_invocation_factory import SirenRouteInvocationFactory
from .serializer import DEFAULT_PROPERTY_SERIALIZER, SirenPropertySerializer

F = TypeVar("F", bound=Callable[..., Any])


class SirenEntityDecorator:
    """Turn a controller method's property mapping into a Siren entity document."""

    def __init__(
        self,
        resource_name: str,
        *,
        operations: tuple[str, ...],
        serializer: SirenPropertySerializer = DEFAULT_PROPERTY_SERIALIZER,
    ):
        if not resource_name.strip():
            raise ValueError("Siren resource name must not be blank")
        self._resource_name = resource_name
        self._operations = operations
        self._serializer = serializer

    def __call__(self, function: F) -> F:
        invocations = SirenRouteInvocationFactory(inspect.signature(function))
        resource_name = self._resource_name
        operations = self._operations
        serializer = self._serializer

        if inspect.iscoroutinefunction(function):

            @wraps(function)
            async def async_wrapper(self: NinjaExtraSirenController, *args: Any, **kwargs: Any) -> dict[str, Any]:
                properties = await function(self, *args, **kwargs)
                if properties is None:
                    raise ValueError("Siren entity documents require properties")
                serialized = dict(serializer.serialize(properties))
                invocation = invocations.create(self, args, kwargs)
                return self.siren_document(resource_name, serialized, operations, invocation.path_values)

            return cast(F, async_wrapper)

        @wraps(function)
        def wrapper(self: NinjaExtraSirenController, *args: Any, **kwargs: Any) -> dict[str, Any]:
            properties = function(self, *args, **kwargs)
            if properties is None:
                raise ValueError("Siren entity documents require properties")
            serialized = dict(serializer.serialize(properties))
            invocation = invocations.create(self, args, kwargs)
            return self.siren_document(resource_name, serialized, operations, invocation.path_values)

        return cast(F, wrapper)
