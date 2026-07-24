from ..contracts import Contract
from .siren_route import SirenRoute


class SirenRoot(Contract):
    route: SirenRoute = SirenRoute(path="/")
    title: str = ""
    version: str = ""
    operations: tuple[str, ...] = ()
