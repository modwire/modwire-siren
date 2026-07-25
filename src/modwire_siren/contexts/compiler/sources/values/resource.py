from modwire_siren.contexts.shared import BaseValue


class Resource(BaseValue):
    reference: str
    name: str
    resource_class: str
    collection_path: str
    entity_path: str | None
    identifier: str
