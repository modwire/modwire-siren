from __future__ import annotations

from collections.abc import Mapping

from pydantic import Field, JsonValue

from ...contracts import Contract
from .action import SirenAction
from .embedded_link import SirenEmbeddedLink
from .link import SirenLink


class SirenDocument(Contract):
    """Represent an official Siren entity document."""

    class_: tuple[str, ...] = Field(default=(), alias="class")
    title: str | None = None
    properties: Mapping[str, JsonValue] = Field(default_factory=dict)
    entities: tuple["SirenEmbeddedLink | SirenEmbeddedRepresentation", ...] = ()
    actions: tuple[SirenAction, ...] = ()
    links: tuple[SirenLink, ...] = ()
