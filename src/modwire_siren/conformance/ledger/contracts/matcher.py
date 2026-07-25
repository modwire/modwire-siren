from abc import ABC, abstractmethod

from ...implementation.values import SirenCapability
from ...specification.values import SirenRequirement
from ..values import SirenConformanceReport


class SirenRequirementMatcher(ABC):
    @abstractmethod
    def match(
        self, requirements: tuple[SirenRequirement, ...], capabilities: tuple[SirenCapability, ...]
    ) -> SirenConformanceReport:
        raise NotImplementedError
