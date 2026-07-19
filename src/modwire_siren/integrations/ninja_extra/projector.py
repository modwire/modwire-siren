from typing import Any, Protocol

from ...contracts.collection import SirenCollectionRequest
from ...contracts.entity import SirenEntityRequest


class SirenProjector(Protocol):

    def document(self, request: SirenEntityRequest) -> dict[str, Any]:
        raise NotImplementedError

    def collection(self, request: SirenCollectionRequest) -> dict[str, Any]:
        raise NotImplementedError


class RequestAwareSirenProjectorFactory(Protocol):

    def for_request(self, request: Any) -> SirenProjector:
        raise NotImplementedError
