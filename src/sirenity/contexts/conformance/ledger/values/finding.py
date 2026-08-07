from sirenity.contexts.conformance.specification.values import SirenRequirement
from sirenity.contexts.shared import BaseValue


class SirenFinding(BaseValue):
    requirement: SirenRequirement
    implemented: bool
    evidence: str
