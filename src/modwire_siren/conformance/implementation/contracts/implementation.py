from abc import ABC, abstractmethod

from ..values import SirenCapability


class SirenImplementation(ABC):
    @abstractmethod
    def capabilities(self) -> tuple[SirenCapability, ...]:
        raise NotImplementedError
