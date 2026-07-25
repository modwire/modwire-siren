from dataclasses import dataclass


@dataclass(frozen=True)
class SirenJunitEvidence:
    identifiers: frozenset[str]
    expected_failures: frozenset[str]
