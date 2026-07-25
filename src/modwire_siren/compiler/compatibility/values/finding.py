from dataclasses import dataclass


@dataclass(frozen=True)
class SirenCompatibilityFinding:
    """Describe one OpenAPI construct outside the current official-Siren boundary."""

    location: str
    category: str
    detail: str
    remediation: str
