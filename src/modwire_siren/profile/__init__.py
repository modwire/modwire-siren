from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .document import ProfileDocument
from .standard import ProfileStandard

__all__ = ["SirenProfile"]


class SirenProfile:
    """Validate, discover, and apply the Modwire Siren UI Profile."""

    def __init__(self):
        self._documents = ProfileDocument(ProfileStandard.load())

    @property
    def identifier(self) -> str:
        """Return the supported profile identifier."""
        return self._documents.standard.identifier

    @property
    def schema_id(self) -> str:
        """Return the public GitHub identifier of the normative schema."""
        return self._documents.standard.schema_id

    @property
    def media_type(self) -> str:
        """Return the profiled Siren response media type."""
        return self._documents.standard.media_type

    def validate(self, metadata: Mapping[str, Any]) -> dict[str, Any]:
        """Validate metadata and apply the normative progressive defaults."""
        return self._documents.validate(metadata)

    def discover(self, document: Mapping[str, Any]) -> dict[str, Any]:
        """Return validated profile metadata from one profiled Siren document."""
        return self._documents.discover(document)

    def enhance(
        self,
        document: Mapping[str, Any],
        metadata: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Apply profile metadata to an OpenAPI-produced or manually assembled Siren document."""
        return self._documents.enhance(document, metadata)
