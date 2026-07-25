from abc import ABC, abstractmethod

from modwire_siren.shared import ModwireSirenError

from ...conformance.implementation.values import SirenCapability
from ...conformance.specification.values import SirenRequirement
from ..values import SirenConformanceReport


class SirenRequirementMatcher(ABC):
    @abstractmethod
    def match(
        self, requirements: tuple[SirenRequirement, ...], capabilities: tuple[SirenCapability, ...]
    ) -> SirenConformanceReport:
        raise ModwireSirenError
