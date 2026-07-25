from abc import ABC, abstractmethod

from modwire_siren.shared import ModwireSirenError

from ....vocabulary import SirenScope
from ...document import SirenDocument
from ..state import SirenProjectionRequest


class SirenScopeProjector(ABC):
    @abstractmethod
    def supports(self, scope: SirenScope) -> bool:
        raise ModwireSirenError

    @abstractmethod
    def project(self, request: SirenProjectionRequest) -> SirenDocument:
        raise ModwireSirenError
