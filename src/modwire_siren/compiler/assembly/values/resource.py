from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceDraft:
    reference: str
    name: str
    resource_class: str
    collection_path: str
    entity_path: str | None
    identifier: str
