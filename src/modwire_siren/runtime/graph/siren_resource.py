from ..contracts import Contract
from .siren_route import SirenRoute


class SirenResource(Contract):
    reference: str
    name: str
    resource_class: str
    identifier: str = "id"
    collection: SirenRoute
    entity: SirenRoute | None = None
    collection_operations: tuple[str, ...] = ()
    entity_operations: tuple[str, ...] = ()
