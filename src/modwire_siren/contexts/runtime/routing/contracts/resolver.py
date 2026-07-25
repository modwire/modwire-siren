from abc import ABC, abstractmethod

from modwire_siren.contexts.graph import SirenApi, SirenResource
from modwire_siren.contexts.shared import ModwireSirenError

from ...request import SirenContext


class SirenResourceResolver(ABC):
    @abstractmethod
    def resolve(self, api: SirenApi, context: SirenContext) -> SirenResource:
        raise ModwireSirenError
