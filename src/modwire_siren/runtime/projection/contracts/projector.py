from abc import ABC, abstractmethod
from typing import Any

from ..values import SirenProjectionRequest


class SirenScopeProjector(ABC):
    @abstractmethod
    def supports(self, scope: str) -> bool:
        pass

    @abstractmethod
    def project(self, request: SirenProjectionRequest) -> dict[str, Any]:
        pass
