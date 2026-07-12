from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from ..error import SirenError
from ..validation.index import SirenIndex
from .references import ProfileReferences
from .standard import ProfileStandard


class ProfileDocument:
    def __init__(self, standard: ProfileStandard):
        self.standard = standard
        self._references = ProfileReferences(standard)

    def validate(self, metadata: Mapping[str, Any]) -> dict[str, Any]:
        try:
            return self.standard.schema.normalize(metadata)
        except SirenError as error:
            raise SirenError("profile.invalid", error.detail, issues=error.issues) from error

    def prepare(
        self,
        document: Mapping[str, Any],
        metadata: Mapping[str, Any],
    ) -> dict[str, Any]:
        normalized = self._authorized(self.validate(metadata), document)
        self._references.validate(normalized, document)
        return normalized

    def enhance(
        self,
        document: Mapping[str, Any],
        metadata: Mapping[str, Any],
    ) -> dict[str, Any]:
        enhanced = deepcopy(dict(document))
        self._reject_existing(enhanced)
        normalized = self.prepare(enhanced, metadata)
        enhanced.setdefault("entities", []).append(
            {
                "class": [self.standard.entity_class],
                "rel": [self.standard.relation],
                "properties": normalized,
                "entities": [],
                "actions": [],
                "links": [],
            }
        )
        enhanced.setdefault("links", []).append(
            {"rel": ["profile"], "href": self.standard.identifier}
        )
        return enhanced

    def discover(self, document: Mapping[str, Any]) -> dict[str, Any]:
        links = [
            link
            for link in SirenIndex.sequence(document.get("links"))
            if "profile" in SirenIndex.strings(link.get("rel"))
        ]
        entities = [
            entity
            for entity in SirenIndex.sequence(document.get("entities"))
            if self.standard.relation in SirenIndex.strings(entity.get("rel"))
        ]
        if len(links) != 1 or len(entities) != 1:
            raise SirenError(
                "profile.discovery",
                "A profiled Siren document requires exactly one profile link and profile entity",
            )
        if links[0].get("href") != self.standard.identifier:
            raise SirenError("profile.unsupported", "The Siren UI profile identifier is unsupported")
        entity = entities[0]
        if (
            self.standard.entity_class not in SirenIndex.strings(entity.get("class"))
            or any(entity.get(name) != [] for name in ("entities", "actions", "links"))
            or "href" in entity
        ):
            raise SirenError("profile.invalid", "The embedded Siren UI profile entity is malformed")
        metadata = entity.get("properties")
        if not isinstance(metadata, Mapping):
            raise SirenError("profile.invalid", "The embedded Siren UI profile properties must be an object")
        normalized = self.validate(metadata)
        self._references.validate(normalized, document)
        return normalized

    def _authorized(
        self,
        metadata: dict[str, Any],
        document: Mapping[str, Any],
    ) -> dict[str, Any]:
        available = set(SirenIndex.named(document.get("actions"), "name"))
        metadata["actions"] = {
            name: action
            for name, action in metadata["actions"].items()
            if name in available
        }
        for region in metadata["presentation"]["layout"]["regions"]:
            region["content"]["actions"] = [
                action
                for action in region["content"]["actions"]
                if action in available
            ]
        return metadata

    def _reject_existing(self, document: Mapping[str, Any]) -> None:
        profile_links = [
            link
            for link in SirenIndex.sequence(document.get("links"))
            if "profile" in SirenIndex.strings(link.get("rel"))
        ]
        profile_entities = [
            entity
            for entity in SirenIndex.sequence(document.get("entities"))
            if self.standard.relation in SirenIndex.strings(entity.get("rel"))
        ]
        if profile_links or profile_entities:
            raise SirenError("profile.ambiguous", "The Siren document is already profiled")
