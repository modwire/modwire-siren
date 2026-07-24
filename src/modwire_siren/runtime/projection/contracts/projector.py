from abc import ABC, abstractmethod

from ...document import SirenDocument
from ..values import SirenProjectionRequest


class SirenScopeProjector(ABC):
    @abstractmethod
    def supports(self, scope: str) -> bool:
        pass

    @abstractmethod
    def project(self, request: SirenProjectionRequest) -> SirenDocument:
        pass
