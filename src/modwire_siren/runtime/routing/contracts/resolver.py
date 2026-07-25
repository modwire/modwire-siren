from abc import ABC, abstractmethod

from modwire_siren.shared import ModwireSirenError

from ...graph import SirenApi, SirenResource
from ...request import SirenContext


class SirenResourceResolver(ABC):
    @abstractmethod
    def resolve(self, api: SirenApi, context: SirenContext) -> SirenResource:
        raise ModwireSirenError
