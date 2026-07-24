from dataclasses import dataclass

from wireup import injectable

from ..values import SirenConformanceReport


@injectable
@dataclass(frozen=True)
class SirenLedgerRenderer:
    def render(self, report: SirenConformanceReport) -> str:
        lines = ["Siren structural contract"]
        for finding in report.findings:
            marker = "✓" if finding.implemented else "✗"
            lines.append(f"{marker} {finding.requirement.label} — {finding.evidence}")
        return "\n".join(lines)
