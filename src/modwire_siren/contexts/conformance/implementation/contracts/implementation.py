from abc import ABC, abstractmethod

from modwire_siren.contexts.shared import ModwireSirenError

from ..values import SirenCapability


class SirenImplementation(ABC):
    @abstractmethod
    def capabilities(self) -> tuple[SirenCapability, ...]:
        raise ModwireSirenError
