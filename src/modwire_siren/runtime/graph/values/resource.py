from modwire_siren.shared import BaseValue

from .route import SirenRoute


class SirenResource(BaseValue):
    reference: str
    name: str
    resource_class: str
    identifier: str = "id"
    collection: SirenRoute
    entity: SirenRoute | None = None
    collection_operations: tuple[str, ...] = ()
    entity_operations: tuple[str, ...] = ()
