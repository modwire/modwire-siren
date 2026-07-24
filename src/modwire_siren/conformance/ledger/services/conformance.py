from dataclasses import dataclass
from pathlib import Path

from wireup import injectable

from ...implementation.contracts import SirenImplementation
from ...specification.contracts import SirenSpecification
from ..contracts import SirenRequirementMatcher
from ..evidence.contracts import SirenBddEvidenceReader
from ..values import SirenConformanceReport
from .renderer import SirenLedgerRenderer


@injectable
@dataclass(frozen=True)
class SirenConformanceService:
    specification: SirenSpecification
    implementation: SirenImplementation
    matcher: SirenRequirementMatcher
    evidence: SirenBddEvidenceReader
    renderer: SirenLedgerRenderer

    def inspect(self, cucumber_report: Path) -> str:
        structural = self.matcher.match(self.specification.requirements(), self.implementation.capabilities())
        report = SirenConformanceReport(structural.findings, self.evidence.read(cucumber_report))
        return self.renderer.render(report)
