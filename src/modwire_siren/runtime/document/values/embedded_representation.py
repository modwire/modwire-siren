from __future__ import annotations

from pydantic import Field

from ...vocabulary import SirenRelation
from .embedded_link import SirenEmbeddedLink
from .entity import SirenEntity


class SirenEmbeddedRepresentation(SirenEntity):
    """Represent a Siren sub-entity embedded in full."""

    rel: tuple[SirenRelation, ...] = Field(min_length=1)
    entities: tuple[SirenEmbeddedLink | SirenEmbeddedRepresentation, ...] | None = None
