from abc import ABC, abstractmethod

from ...siren_context import SirenContext
from ...siren_resource import SirenResource


class SirenCapabilityValidator(ABC):
    @abstractmethod
    def validate(self, resource: SirenResource, context: SirenContext) -> None:
        pass
