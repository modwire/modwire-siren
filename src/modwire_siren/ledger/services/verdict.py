from dataclasses import dataclass

from wireup import injectable

from ..values import SirenConformanceReport


@injectable
@dataclass(frozen=True)
class SirenLedgerVerdict:
    def verify(self, report: SirenConformanceReport) -> None:
        unimplemented = tuple(finding.requirement.label for finding in report.findings if not finding.implemented)
        if unimplemented:
            labels = ", ".join(unimplemented)
            raise ValueError(f"Siren conformance ledger has unimplemented structural requirements: {labels}.")
