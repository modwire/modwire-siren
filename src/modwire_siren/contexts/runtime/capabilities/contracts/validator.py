from abc import ABC, abstractmethod

from modwire_siren.contexts.shared import ModwireSirenError

from ...graph import SirenResource
from ...request import SirenContext


class SirenCapabilityValidator(ABC):
    @abstractmethod
    def validate(self, resource: SirenResource, context: SirenContext) -> None:
        raise ModwireSirenError
