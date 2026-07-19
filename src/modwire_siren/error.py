from typing import Any


class SirenError(ValueError):

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
        return {"kind": self.kind, "detail": self.detail, "issues": list(self.issues)}
