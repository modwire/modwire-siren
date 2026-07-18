from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class RelatedLinkInput:
    """Describe one application-owned related link for Siren projection."""

    rel: str
    resource: str
    value: Any | Sequence[Any]
