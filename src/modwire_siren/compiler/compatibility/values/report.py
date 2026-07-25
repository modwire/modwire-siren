from dataclasses import dataclass

from .finding import SirenCompatibilityFinding


@dataclass(frozen=True)
class SirenCompatibilityReport:
    """Expose deterministic OpenAPI-to-Siren compatibility findings."""

    findings: tuple[SirenCompatibilityFinding, ...]

    @property
    def compatible(self) -> bool:
        return not self.findings

    def render(self) -> str:
        if self.compatible:
            return "OpenAPI-to-Siren compatibility: compatible"
        rows = (
            f"- {finding.location} [{finding.category}]: {finding.detail}. Remediation: {finding.remediation}"
            for finding in self.findings
        )
        return "OpenAPI-to-Siren compatibility findings:\n" + "\n".join(rows)
