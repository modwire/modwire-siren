from typing import Any, Protocol

from ...contracts.collection import SirenCollectionRequest
from ...contracts.entity import SirenEntityRequest


class SirenProjector(Protocol):
    """Project Siren requests without depending on a concrete composition root."""

    def document(self, request: SirenEntityRequest) -> dict[str, Any]:
        raise NotImplementedError

    def collection(self, request: SirenCollectionRequest) -> dict[str, Any]:
        raise NotImplementedError


class RequestAwareSirenProjectorFactory(Protocol):
    """Create a Siren projector for the current web request."""

    def for_request(self, request: Any) -> SirenProjector:
        raise NotImplementedError
