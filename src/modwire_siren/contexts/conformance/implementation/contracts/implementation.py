from abc import ABC, abstractmethod

from modwire_siren.shared import ModwireSirenError

from ..values import SirenCapability


class SirenImplementation(ABC):
    @abstractmethod
    def capabilities(self) -> tuple[SirenCapability, ...]:
        raise ModwireSirenError
