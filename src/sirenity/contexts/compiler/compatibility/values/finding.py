from sirenity.contexts.shared import BaseValue


class SirenCompatibilityFinding(BaseValue):
    """Describe one OpenAPI construct outside the current official-Siren boundary."""

    location: str
    category: str
    detail: str
    remediation: str
