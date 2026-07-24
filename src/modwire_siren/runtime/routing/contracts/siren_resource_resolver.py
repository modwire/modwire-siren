from abc import ABC, abstractmethod

from ...siren_api import SirenApi
from ...siren_context import SirenContext
from ...siren_resource import SirenResource


class SirenResourceResolver(ABC):
    @abstractmethod
    def resolve(self, api: SirenApi, context: SirenContext) -> SirenResource:
        pass
