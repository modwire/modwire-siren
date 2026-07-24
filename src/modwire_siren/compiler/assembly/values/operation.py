from dataclasses import dataclass

from ....runtime.vocabulary import SirenHttpMethod, SirenScope


@dataclass(frozen=True)
class OperationDraft:
    resource: str | None
    scope: SirenScope
    name: str
    method: SirenHttpMethod
    path: str
    media_type: str | None
