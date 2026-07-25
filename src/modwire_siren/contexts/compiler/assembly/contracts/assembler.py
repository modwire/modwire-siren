from abc import ABC, abstractmethod

from modwire_siren.contexts.runtime.graph import SirenApi
from modwire_siren.shared import ModwireSirenError


class SirenApiAssembler(ABC):
    @abstractmethod
    def assemble(self, apis: tuple[SirenApi, ...]) -> SirenApi:
        raise ModwireSirenError
