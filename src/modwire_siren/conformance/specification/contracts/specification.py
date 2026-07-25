from abc import ABC, abstractmethod

from modwire_siren.shared import ModwireSirenError

from ..values import SirenRequirement


class SirenSpecification(ABC):
    @abstractmethod
    def requirements(self) -> tuple[SirenRequirement, ...]:
        raise ModwireSirenError
