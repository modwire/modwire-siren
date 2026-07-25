from modwire_siren.shared import BaseValue, SirenHttpMethod, SirenMediaType, SirenScope


class OperationDraft(BaseValue):
    resource: str | None
    scope: SirenScope
    name: str
    method: SirenHttpMethod
    path: str
    media_type: SirenMediaType | None
