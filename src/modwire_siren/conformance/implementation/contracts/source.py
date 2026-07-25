from abc import ABC, abstractmethod

from ..values import SirenCapability


class SirenContractSource(ABC):
    @abstractmethod
    def capability(self) -> SirenCapability:
        raise NotImplementedError
