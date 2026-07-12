from typing import Any


class SirenError(ValueError):
    """Report one invalid Siren contract with structured issue details."""

    def __init__(
        self,
        kind: str,
        detail: str,
        *,
        issues: tuple[dict[str, str], ...] = (),
    ):
        self.kind = kind
        self.detail = detail
        self.issues = issues
        super().__init__(detail)

    def as_dict(self) -> dict[str, Any]:
        """Serialize the complete Siren error for API and MCP boundaries."""
        return {"kind": self.kind, "detail": self.detail, "issues": list(self.issues)}
