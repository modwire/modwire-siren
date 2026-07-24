from dataclasses import dataclass


@dataclass
class OperationDraft:
    resource: str | None
    scope: str
    name: str
    method: str
    path: str
    media_type: str | None
