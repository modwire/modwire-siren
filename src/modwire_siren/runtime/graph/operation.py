from ..contracts import Contract
from ..vocabulary import SirenHttpMethod, SirenScope
from .field import SirenField
from .route import SirenRoute


class SirenOperation(Contract):
    name: str
    resource: str | None = None
    scope: SirenScope
    method: SirenHttpMethod
    route: SirenRoute
    media_type: str | None = None
    fields: tuple[SirenField, ...] = ()
