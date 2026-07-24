from abc import ABC, abstractmethod

from ...graph import SirenApi, SirenResource
from ...request import SirenContext


class SirenResourceResolver(ABC):
    @abstractmethod
    def resolve(self, api: SirenApi, context: SirenContext) -> SirenResource:
        pass
