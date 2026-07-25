from modwire_siren.contexts.shared import BaseValue


class ResourceDraft(BaseValue):
    reference: str
    name: str
    resource_class: str
    collection_path: str
    entity_path: str | None
    identifier: str
