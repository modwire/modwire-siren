from modwire_siren.contexts.shared import BaseValue, SirenHttpMethod, SirenMediaType, SirenScope

from .field import SirenField
from .response import SirenResponse
from .route import SirenRoute


class SirenOperation(BaseValue):
    name: str
    resource: str | None = None
    scope: SirenScope
    method: SirenHttpMethod
    route: SirenRoute
    media_type: SirenMediaType | None = None
    fields: tuple[SirenField, ...] = ()
    responses: tuple[SirenResponse, ...] = ()
