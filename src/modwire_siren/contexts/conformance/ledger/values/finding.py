from modwire_siren.contexts.conformance.specification.values import SirenRequirement
from modwire_siren.shared import BaseValue


class SirenFinding(BaseValue):
    requirement: SirenRequirement
    implemented: bool
    evidence: str
