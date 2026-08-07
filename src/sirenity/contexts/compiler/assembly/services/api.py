from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from wireup import injectable

from sirenity.contexts.graph import SirenApi

from ...compatibility import SirenCompatibilityReport
from ...sources import SirenSource
from ..contracts import SirenApiAssembler


@injectable
@dataclass(frozen=True)
class SirenApiService:
    """Build a validated Siren API graph from one or more sources."""

    sources: Sequence[SirenSource]
    assembler: SirenApiAssembler

    def build(
        self, schema: dict[str, Any], source_path: str = "/", public_path: str = "/"
    ) -> SirenApi:
        return self.assembler.assemble(
            tuple(source.load(schema, source_path, public_path) for source in self.sources)
        )

    def audit(self, schema: dict[str, Any]) -> SirenCompatibilityReport:
        findings = tuple(finding for source in self.sources for finding in source.audit(schema))
        ordered = sorted(findings, key=lambda finding: (finding.location, finding.category))
        return SirenCompatibilityReport(findings=tuple(ordered))
