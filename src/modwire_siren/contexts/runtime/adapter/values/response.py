from collections.abc import Mapping

from pydantic import Field, JsonValue

from modwire_siren.contexts.shared import BaseValue


class SirenAdapterResponse(BaseValue):
    """Represent an HTTP-ready official Siren response without framework dependencies."""

    status: int
    payload: Mapping[str, JsonValue]
    media_type: str = "application/vnd.siren+json"
    headers: Mapping[str, str] = Field(default_factory=dict)
