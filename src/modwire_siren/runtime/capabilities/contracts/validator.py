from abc import ABC, abstractmethod

from ...graph import SirenResource
from ...request import SirenContext


class SirenCapabilityValidator(ABC):
    @abstractmethod
    def validate(self, resource: SirenResource, context: SirenContext) -> None:
        pass
