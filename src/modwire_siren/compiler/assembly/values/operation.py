from dataclasses import dataclass

from ....vocabulary import SirenHttpMethod, SirenMediaType, SirenScope


@dataclass(frozen=True)
class OperationDraft:
    resource: str | None
    scope: SirenScope
    name: str
    method: SirenHttpMethod
    path: str
    media_type: SirenMediaType | None
