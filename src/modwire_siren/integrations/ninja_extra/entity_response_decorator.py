import inspect
from collections.abc import Callable, Mapping
from functools import wraps
from typing import Any, TypeVar, cast

from .controller import NinjaExtraSirenController
from .entity_policy import EntityOperationSelection, EntityRelatedLinkSelection, SirenEntityPolicyResolver
from .no_policy import NO_SIREN_POLICY
from .response import EMPTY_HEADERS, NinjaExtraSirenResponse
from .route_invocation import SirenRouteInvocation
from .route_invocation_factory import SirenRouteInvocationFactory
from .serializer import DEFAULT_PROPERTY_SERIALIZER, SirenPropertySerializer

F = TypeVar("F", bound=Callable[..., Any])


class SirenEntityResponseDecorator:
    def __init__(
        self,
        resource_name: str,
        *,
        operations: EntityOperationSelection = (),
        related_links: EntityRelatedLinkSelection = (),
        policy: Any = NO_SIREN_POLICY,
        status_code: int = 200,
        headers: Mapping[str, str] = EMPTY_HEADERS,
        serializer: SirenPropertySerializer = DEFAULT_PROPERTY_SERIALIZER,
    ):
        if not resource_name.strip():
            raise ValueError("Siren resource name must not be blank")
        self._resource_name = resource_name
        self._operations = operations
        self._related_links = related_links
        self._policy = policy
        self._status_code = status_code
        self._headers = dict(headers)
        self._serializer = serializer
        self._policies = SirenEntityPolicyResolver()

    def __call__(self, function: F) -> F:
        invocations = SirenRouteInvocationFactory(inspect.signature(function))
        resource_name = self._resource_name
        operations = self._operations
        related_links = self._related_links
        policy = self._policy
        status_code = self._status_code
        headers = self._headers
        serializer = self._serializer
        policies = self._policies

        def response(
            controller: NinjaExtraSirenController,
            properties: Any,
            invocation: SirenRouteInvocation,
        ) -> NinjaExtraSirenResponse:
            if status_code == 204:
                if properties is not None:
                    raise ValueError("204 Siren responses must not include a body")
                return controller.siren_responses.no_content(headers=headers)
            if properties is None:
                raise ValueError("Siren entity responses require properties")
            serialized = dict(serializer.serialize(properties))
            return controller.siren_response(
                resource_name,
                serialized,
                operation_ids=policies.operations(policy, operations, invocation.request, resource_name, serialized),
                path_values=invocation.path_values,
                related_links=policies.related_links(
                    policy,
                    related_links,
                    invocation.request,
                    resource_name,
                    serialized,
                ),
                status_code=status_code,
                headers=headers,
            )

        if inspect.iscoroutinefunction(function):

            @wraps(function)
            async def async_wrapper(
                self: NinjaExtraSirenController, *args: Any, **kwargs: Any
            ) -> NinjaExtraSirenResponse:
                properties = await function(self, *args, **kwargs)
                invocation = invocations.create(self, args, kwargs)
                return response(self, properties, invocation)

            return cast(F, async_wrapper)

        @wraps(function)
        def wrapper(self: NinjaExtraSirenController, *args: Any, **kwargs: Any) -> NinjaExtraSirenResponse:
            properties = function(self, *args, **kwargs)
            invocation = invocations.create(self, args, kwargs)
            return response(self, properties, invocation)

        return cast(F, wrapper)
