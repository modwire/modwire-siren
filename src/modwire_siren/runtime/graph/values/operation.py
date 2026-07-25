from modwire_siren.shared import BaseValue

from ....vocabulary import SirenHttpMethod, SirenMediaType, SirenScope
from .field import SirenField
from .route import SirenRoute


class SirenOperation(BaseValue):
    name: str
    resource: str | None = None
    scope: SirenScope
    method: SirenHttpMethod
    route: SirenRoute
    media_type: SirenMediaType | None = None
    fields: tuple[SirenField, ...] = ()
