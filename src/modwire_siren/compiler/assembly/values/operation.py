from dataclasses import dataclass

from modwire_siren.shared import SirenHttpMethod, SirenMediaType, SirenScope


@dataclass(frozen=True)
class OperationDraft:
    resource: str | None
    scope: SirenScope
    name: str
    method: SirenHttpMethod
    path: str
    media_type: SirenMediaType | None
