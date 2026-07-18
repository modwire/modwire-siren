import inspect
from collections.abc import Callable, Mapping
from functools import wraps
from typing import Any, TypeVar, cast

from ...contracts.collection import (
    DEFAULT_PAGINATION,
    CustomPagination,
    NoPagination,
    OffsetPagination,
    SirenCollectionRequest,
)
from .collection_policy import CollectionOperationSelection, SirenCollectionPolicyResolver
from .no_policy import NO_SIREN_POLICY
from .response import EMPTY_HEADERS, NinjaExtraSirenResponse
from .route_invocation import SirenRouteInvocation
from .route_invocation_factory import SirenRouteInvocationFactory
from .serializer import DEFAULT_PROPERTY_SERIALIZER, SirenPropertySerializer, serialize_collection_items

F = TypeVar("F", bound=Callable[..., Any])


class SirenCollectionResponseDecorator:
    def __init__(
        self,
        resource_name: str,
        *,
        operations: CollectionOperationSelection = (),
        item_operations: tuple[str, ...] = (),
        policy: Any = NO_SIREN_POLICY,
        pagination: NoPagination | OffsetPagination | CustomPagination = DEFAULT_PAGINATION,
        status_code: int = 200,
        headers: Mapping[str, str] = EMPTY_HEADERS,
        serializer: SirenPropertySerializer = DEFAULT_PROPERTY_SERIALIZER,
    ):
        if not resource_name.strip():
            raise ValueError("Siren resource name must not be blank")
        self._resource_name = resource_name
        self._operations = operations
        self._item_operations = item_operations
        self._policy = policy
        self._pagination = pagination
        self._status_code = status_code
        self._headers = dict(headers)
        self._serializer = serializer
        self._policies = SirenCollectionPolicyResolver()

    def __call__(self, function: F) -> F:
        invocations = SirenRouteInvocationFactory(inspect.signature(function))
        resource_name = self._resource_name
        operations = self._operations
        item_operations = self._item_operations
        policy = self._policy
        pagination = self._pagination
        status_code = self._status_code
        headers = self._headers
        serializer = self._serializer
        policies = self._policies

        def response(self, items: Any, invocation: SirenRouteInvocation) -> NinjaExtraSirenResponse:
            if status_code == 204:
                if items is not None:
                    raise ValueError("204 Siren responses must not include a body")
                return self.siren_responses.no_content(headers=headers)
            if items is None:
                raise ValueError("Siren collection responses require items")
            serialized = serialize_collection_items(serializer, items)
            return self.siren_collection_response(
                SirenCollectionRequest(
                    resource_name=resource_name,
                    items=serialized,
                    collection_operation_ids=policies.operations(policy, operations, invocation.request, resource_name),
                    item_operation_ids=item_operations,
                    path_values=invocation.path_values,
                    pagination=pagination,
                ),
                status_code=status_code,
                headers=headers,
            )

        if inspect.iscoroutinefunction(function):

            @wraps(function)
            async def async_wrapper(self, *args: Any, **kwargs: Any) -> NinjaExtraSirenResponse:
                items = await function(self, *args, **kwargs)
                invocation = invocations.create(self, args, kwargs)
                return response(self, items, invocation)

            return cast(F, async_wrapper)

        @wraps(function)
        def wrapper(self, *args: Any, **kwargs: Any) -> NinjaExtraSirenResponse:
            items = function(self, *args, **kwargs)
            invocation = invocations.create(self, args, kwargs)
            return response(self, items, invocation)

        return cast(F, wrapper)


def siren_collection(
    *,
    resource: str,
    operations: CollectionOperationSelection = (),
    item_operations: tuple[str, ...] = (),
    policy: Any = NO_SIREN_POLICY,
    pagination: NoPagination | OffsetPagination | CustomPagination = DEFAULT_PAGINATION,
    status_code: int = 200,
    headers: Mapping[str, str] = EMPTY_HEADERS,
    serializer: SirenPropertySerializer = DEFAULT_PROPERTY_SERIALIZER,
) -> Callable[[F], F]:
    """Turn a controller method's item mappings into a Siren collection response payload."""
    return SirenCollectionResponseDecorator(
        resource,
        operations=operations,
        item_operations=item_operations,
        policy=policy,
        pagination=pagination,
        status_code=status_code,
        headers=headers,
        serializer=serializer,
    )
