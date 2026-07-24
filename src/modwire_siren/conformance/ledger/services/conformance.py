from dataclasses import dataclass

from wireup import injectable

from ...implementation.contracts import SirenImplementation
from ...specification.contracts import SirenSpecification
from ..contracts import SirenRequirementMatcher
from ..values import SirenConformanceReport
from .renderer import SirenLedgerRenderer


@injectable
@dataclass(frozen=True)
class SirenConformanceService:
    specification: SirenSpecification
    implementation: SirenImplementation
    matcher: SirenRequirementMatcher
    renderer: SirenLedgerRenderer

    def inspect(self) -> SirenConformanceReport:
        return self.matcher.match(self.specification.requirements(), self.implementation.capabilities())

    def render(self) -> str:
        return self.renderer.render(self.inspect())
