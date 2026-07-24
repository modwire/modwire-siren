from __future__ import annotations

from collections.abc import Mapping

from pydantic import Field, JsonValue

from ...contracts import Contract
from .action import SirenAction
from .embedded_link import SirenEmbeddedLink
from .embedded_representation import SirenEmbeddedRepresentation
from .link import SirenLink


class SirenDocument(Contract):
    """Represent an official Siren entity document.

    Project an engine request into this immutable public value, then serialize it with
    `model_dump(by_alias=True, mode="json", exclude_none=True)` for an
    `application/vnd.siren+json` response. Navigation belongs in `links`; embedded sub-entities
    belong in `entities`.
    """

    class_: tuple[str, ...] | None = Field(default=None, alias="class")
    title: str | None = None
    properties: Mapping[str, JsonValue] | None = None
    entities: tuple[SirenEmbeddedLink | SirenEmbeddedRepresentation, ...] | None = None
    actions: tuple[SirenAction, ...] | None = None
    links: tuple[SirenLink, ...] | None = None
