from __future__ import annotations

from collections.abc import Mapping

from pydantic import Field, JsonValue

from ...contracts import Contract
from .action import SirenAction
from .embedded_link import SirenEmbeddedLink
from .link import SirenLink


class SirenEmbeddedRepresentation(Contract):
    """Represent a Siren sub-entity embedded in full."""

    class_: tuple[str, ...] | None = Field(default=None, alias="class")
    rel: tuple[str, ...] = Field(min_length=1)
    title: str | None = None
    properties: Mapping[str, JsonValue] | None = None
    entities: tuple[SirenEmbeddedLink | SirenEmbeddedRepresentation, ...] | None = None
    actions: tuple[SirenAction, ...] | None = None
    links: tuple[SirenLink, ...] | None = None
