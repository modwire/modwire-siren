from abc import ABC, abstractmethod

from ....runtime import SirenApi


class SirenApiAssembler(ABC):
    @abstractmethod
    def assemble(self, apis: tuple[SirenApi, ...]) -> SirenApi:
        raise NotImplementedError
