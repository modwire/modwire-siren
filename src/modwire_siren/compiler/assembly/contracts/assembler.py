from abc import ABC, abstractmethod

from modwire_siren.shared import ModwireSirenError

from ....runtime.graph import SirenApi


class SirenApiAssembler(ABC):
    @abstractmethod
    def assemble(self, apis: tuple[SirenApi, ...]) -> SirenApi:
        raise ModwireSirenError
