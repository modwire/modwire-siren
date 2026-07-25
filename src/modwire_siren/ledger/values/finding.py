from modwire_siren.shared import BaseValue

from ...conformance.specification.values import SirenRequirement


class SirenFinding(BaseValue):
    requirement: SirenRequirement
    implemented: bool
    evidence: str
