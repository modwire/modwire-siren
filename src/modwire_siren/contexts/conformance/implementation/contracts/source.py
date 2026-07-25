from abc import ABC, abstractmethod

from modwire_siren.contexts.shared import ModwireSirenError

from ..values import SirenCapability


class SirenContractSource(ABC):
    @abstractmethod
    def capabilities(self) -> tuple[SirenCapability, ...]:
        raise ModwireSirenError
