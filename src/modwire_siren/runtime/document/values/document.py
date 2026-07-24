from __future__ import annotations

from collections.abc import Mapping

from pydantic import Field, JsonValue

from ...contracts import Contract
from .action import SirenAction
from .embedded_link import SirenEmbeddedLink
from .embedded_representation import SirenEmbeddedRepresentation
from .link import SirenLink


class SirenDocument(Contract):
    """Represent an official Siren entity document."""

    class_: tuple[str, ...] | None = Field(default=None, alias="class")
    title: str | None = None
    properties: Mapping[str, JsonValue] | None = None
    entities: tuple[SirenEmbeddedLink | SirenEmbeddedRepresentation, ...] | None = None
    actions: tuple[SirenAction, ...] | None = None
    links: tuple[SirenLink, ...] | None = None
