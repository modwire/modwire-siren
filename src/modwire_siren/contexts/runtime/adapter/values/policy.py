from typing import Literal

from modwire_siren.contexts.runtime.request import SirenRelationship
from modwire_siren.contexts.shared import BaseValue


class SirenAdapterPolicy(BaseValue):
    """Declare application-owned projection semantics and permitted capabilities.

    Adapters never infer permissions or representation semantics from OpenAPI or result identifiers.
    Supply this value directly to a framework-neutral request, or return it from a framework bridge's
    capability policy. For a collection response, `item_titles` supplies one explicit title per
    result item in the same order as `item_capabilities`.
    """

    title: str | None = None
    representation: Literal["root", "entity", "collection", "command"] | None = None
    capabilities: frozenset[str] = frozenset()
    item_titles: tuple[str, ...] = ()
    item_capabilities: tuple[frozenset[str], ...] = ()
    relationships: tuple[SirenRelationship, ...] = ()
