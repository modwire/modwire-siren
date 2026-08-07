from abc import ABC, abstractmethod

from sirenity.contexts.graph import SirenApi, SirenResource
from sirenity.contexts.shared import ModwireSirenError

from ...request import SirenContext


class SirenResourceResolver(ABC):
    @abstractmethod
    def resolve(self, api: SirenApi, context: SirenContext) -> SirenResource:
        raise ModwireSirenError
