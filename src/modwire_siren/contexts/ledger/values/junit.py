from modwire_siren.shared import BaseValue


class SirenJunitEvidence(BaseValue):
    identifiers: frozenset[str]
    expected_failures: frozenset[str]
