from abc import ABC, abstractmethod

from sirenity.contexts.shared import ModwireSirenError

from ..values import SirenCapability


class SirenContractSource(ABC):
    @abstractmethod
    def capabilities(self) -> tuple[SirenCapability, ...]:
        raise ModwireSirenError
