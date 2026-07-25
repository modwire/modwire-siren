from abc import ABC, abstractmethod

from modwire_siren.contexts.shared import ModwireSirenError

from ..values import SirenCapability


class SirenContractSource(ABC):
    @abstractmethod
    def capability(self) -> SirenCapability:
        raise ModwireSirenError
