from modwire_siren.contexts.shared import BaseValue, SirenHttpMethod, SirenMediaType, SirenScope

from .response_draft import ResponseDraft


class OperationDraft(BaseValue):
    resource: str | None
    scope: SirenScope
    name: str
    method: SirenHttpMethod
    path: str
    media_type: SirenMediaType | None
    responses: tuple[ResponseDraft, ...] = ()
