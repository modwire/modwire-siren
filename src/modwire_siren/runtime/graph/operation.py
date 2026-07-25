from ...vocabulary import SirenHttpMethod, SirenMediaType, SirenScope
from ..contracts import Contract
from .field import SirenField
from .route import SirenRoute


class SirenOperation(Contract):
    name: str
    resource: str | None = None
    scope: SirenScope
    method: SirenHttpMethod
    route: SirenRoute
    media_type: SirenMediaType | None = None
    fields: tuple[SirenField, ...] = ()
