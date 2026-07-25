from dataclasses import dataclass

from ...conformance.specification.values import SirenRequirement


@dataclass(frozen=True)
class SirenFinding:
    requirement: SirenRequirement
    implemented: bool
    evidence: str
