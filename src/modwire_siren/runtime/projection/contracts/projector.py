from abc import ABC, abstractmethod

from ...document import SirenDocument
from ...vocabulary import SirenScope
from ..values import SirenProjectionRequest


class SirenScopeProjector(ABC):
    @abstractmethod
    def supports(self, scope: SirenScope) -> bool:
        pass

    @abstractmethod
    def project(self, request: SirenProjectionRequest) -> SirenDocument:
        pass
