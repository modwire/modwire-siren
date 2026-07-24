from typing import Literal

from .contract import Contract
from .siren_field import SirenField
from .siren_route import SirenRoute


class SirenOperation(Contract):
    name: str
    resource: str | None = None
    scope: Literal["root", "collection", "entity"]
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
    route: SirenRoute
    media_type: str | None = None
    fields: tuple[SirenField, ...] = ()
