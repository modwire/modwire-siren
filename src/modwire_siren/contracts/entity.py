from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field, model_serializer

from .action import SirenAction
from .base import SirenContract
from .link import SirenLink
from .related_link import RelatedLinkInput


class SirenEntity(SirenContract):
    classes: Annotated[tuple[str, ...], Field(serialization_alias="class")]
    properties: dict[str, Any]
    links: tuple[SirenLink, ...]
    actions: tuple[SirenAction, ...]
    entities: tuple[SirenEmbeddedEntity, ...]


class SirenEmbeddedEntity(SirenContract):
    rel: tuple[str, ...]
    entity: SirenEntity

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {"rel": self.rel, **self.entity.model_dump(mode="json", by_alias=True)}


class SirenEntityRequest(SirenContract):
    """Describe the resource data and allowed operations projected into one entity."""

    resource_name: str
    properties: dict[str, Any]
    operation_ids: tuple[str, ...]
    path_values: dict[str, Any]
    entities: tuple[SirenEmbeddedEntity, ...]
    related_links: tuple[RelatedLinkInput, ...] = ()


SirenEntity.model_rebuild()
