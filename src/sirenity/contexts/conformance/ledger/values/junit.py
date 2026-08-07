from sirenity.contexts.shared import BaseValue


class SirenJunitEvidence(BaseValue):
    identifiers: frozenset[str]
    expected_failures: frozenset[str]
