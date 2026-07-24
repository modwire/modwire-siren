from dataclasses import dataclass
from pathlib import Path

from wireup import injectable

from ...implementation.contracts import SirenImplementation
from ...specification.contracts import SirenSpecification
from ..contracts import SirenRequirementMatcher
from ..evidence.contracts import SirenBddEvidenceReader
from ..values import SirenConformanceReport
from .renderer import SirenLedgerRenderer
from .verdict import SirenLedgerVerdict


@injectable
@dataclass(frozen=True)
class SirenConformanceService:
    specification: SirenSpecification
    implementation: SirenImplementation
    matcher: SirenRequirementMatcher
    evidence: SirenBddEvidenceReader
    renderer: SirenLedgerRenderer
    verdict: SirenLedgerVerdict

    def inspect(self, cucumber_report: Path) -> SirenConformanceReport:
        structural = self.matcher.match(self.specification.requirements(), self.implementation.capabilities())
        return SirenConformanceReport(structural.findings, self.evidence.read(cucumber_report))

    def render(self, report: SirenConformanceReport) -> str:
        return self.renderer.render(report)

    def verify(self, report: SirenConformanceReport) -> None:
        self.verdict.verify(report)
