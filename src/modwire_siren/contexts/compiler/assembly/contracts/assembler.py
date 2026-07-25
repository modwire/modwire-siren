from abc import ABC, abstractmethod

from modwire_siren.contexts.graph import SirenApi
from modwire_siren.contexts.shared import ModwireSirenError


class SirenApiAssembler(ABC):
    @abstractmethod
    def assemble(self, apis: tuple[SirenApi, ...]) -> SirenApi:
        raise ModwireSirenError
