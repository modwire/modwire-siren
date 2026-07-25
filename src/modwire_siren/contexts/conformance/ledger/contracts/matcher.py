from abc import ABC, abstractmethod

from modwire_siren.contexts.conformance.implementation.values import SirenCapability
from modwire_siren.contexts.conformance.specification.values import SirenRequirement
from modwire_siren.contexts.shared import ModwireSirenError

from ..values import SirenConformanceReport


class SirenRequirementMatcher(ABC):
    @abstractmethod
    def match(
        self, requirements: tuple[SirenRequirement, ...], capabilities: tuple[SirenCapability, ...]
    ) -> SirenConformanceReport:
        raise ModwireSirenError
