from abc import ABC, abstractmethod

from sirenity.contexts.shared import ModwireSirenError, SirenScope

from ...document import SirenDocument
from ..state import SirenProjectionRequest


class SirenScopeProjector(ABC):
    @abstractmethod
    def supports(self, scope: SirenScope) -> bool:
        raise ModwireSirenError

    @abstractmethod
    def project(self, request: SirenProjectionRequest) -> SirenDocument:
        raise ModwireSirenError
