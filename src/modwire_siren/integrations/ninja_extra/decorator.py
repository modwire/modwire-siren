from collections.abc import Callable, Mapping
from typing import Any, TypeVar

from .entity_policy import EntityOperationSelection, EntityRelatedLinkSelection
from .entity_response_decorator import SirenEntityResponseDecorator
from .no_policy import NO_SIREN_POLICY
from .response import EMPTY_HEADERS
from .serializer import DEFAULT_PROPERTY_SERIALIZER, SirenPropertySerializer

F = TypeVar("F", bound=Callable[..., Any])


def siren_entity(
    *,
    resource: str,
    operations: EntityOperationSelection = (),
    related_links: EntityRelatedLinkSelection = (),
    policy: Any = NO_SIREN_POLICY,
    status_code: int = 200,
    headers: Mapping[str, str] = EMPTY_HEADERS,
    serializer: SirenPropertySerializer = DEFAULT_PROPERTY_SERIALIZER,
) -> Callable[[F], F]:
    """Turn a controller method's property mapping into a Siren response payload."""
    return SirenEntityResponseDecorator(
        resource,
        operations=operations,
        related_links=related_links,
        policy=policy,
        status_code=status_code,
        headers=headers,
        serializer=serializer,
    )
