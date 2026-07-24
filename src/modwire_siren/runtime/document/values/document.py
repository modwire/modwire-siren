from __future__ import annotations

from .embedded_link import SirenEmbeddedLink
from .embedded_representation import SirenEmbeddedRepresentation
from .entity import SirenEntity


class SirenDocument(SirenEntity):
    """Represent an official Siren entity document.

    Project an engine request into this immutable public value, then serialize it with
    `model_dump(by_alias=True, mode="json", exclude_none=True)` for an
    `application/vnd.siren+json` response. Navigation belongs in `links`; embedded sub-entities
    belong in `entities`.
    """

    entities: tuple[SirenEmbeddedLink | SirenEmbeddedRepresentation, ...] | None = None
