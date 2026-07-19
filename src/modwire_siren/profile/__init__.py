from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .document import ProfileDocument
from .standard import ProfileStandard

__all__ = ["SirenProfile"]


class SirenProfile:

    def __init__(self):
        self._documents = ProfileDocument(ProfileStandard.load())

    @property
    def identifier(self) -> str:
        return self._documents.standard.identifier

    @property
    def schema_id(self) -> str:
        return self._documents.standard.schema_id

    @property
    def media_type(self) -> str:
        return self._documents.standard.media_type

    def validate(self, metadata: Mapping[str, Any]) -> dict[str, Any]:
        return self._documents.validate(metadata)

    def discover(self, document: Mapping[str, Any]) -> dict[str, Any]:
        return self._documents.discover(document)

    def enhance(
        self,
        document: Mapping[str, Any],
        metadata: Mapping[str, Any],
    ) -> dict[str, Any]:
        return self._documents.enhance(document, metadata)
