from dataclasses import dataclass

from .finding import SirenFinding


@dataclass(frozen=True)
class SirenConformanceReport:
    findings: tuple[SirenFinding, ...]
