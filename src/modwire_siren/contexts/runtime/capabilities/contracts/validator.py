from abc import ABC, abstractmethod

from modwire_siren.contexts.graph import SirenResource
from modwire_siren.contexts.shared import ModwireSirenError

from ...request import SirenContext


class SirenCapabilityValidator(ABC):
    @abstractmethod
    def validate(self, resource: SirenResource, context: SirenContext) -> None:
        raise ModwireSirenError
