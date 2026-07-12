from collections.abc import Mapping
from typing import Any


class SirenClientError(RuntimeError):
    """Report navigation, affordance, transport, and remote problem failures."""

    def __init__(self, kind: str, detail: str, **context: Any):
        self.kind = kind
        self.detail = detail
        self.context = context
        super().__init__(detail)

    def as_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "detail": self.detail, **self.context}

    @classmethod
    def problem(cls, status_code: int, document: Mapping[str, Any]) -> "SirenClientError":
        body = dict(document)
        return cls(
            "remote-problem",
            str(body.get("detail") or body.get("title") or "Siren request failed."),
            status=status_code,
            title=body.get("title"),
            body=body,
        )
