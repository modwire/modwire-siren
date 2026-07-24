from pydantic import Field

from .contract import Contract
from .siren_route import SirenRoute


class SirenRoot(Contract):
    route: SirenRoute = Field(default_factory=lambda: SirenRoute(path="/"))
    title: str = ""
    version: str = ""
    operations: tuple[str, ...] = ()
