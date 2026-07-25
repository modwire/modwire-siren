from abc import ABC, abstractmethod

from ....vocabulary import SirenScope
from ...document import SirenDocument
from ..values import SirenProjectionRequest


class SirenScopeProjector(ABC):
    @abstractmethod
    def supports(self, scope: SirenScope) -> bool:
        raise NotImplementedError

    @abstractmethod
    def project(self, request: SirenProjectionRequest) -> SirenDocument:
        raise NotImplementedError
