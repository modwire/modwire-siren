from ..contracts import Contract
from .route import SirenRoute


class SirenRoot(Contract):
    route: SirenRoute = SirenRoute(path="/")
    title: str = ""
    version: str = ""
    operations: tuple[str, ...] = ()
