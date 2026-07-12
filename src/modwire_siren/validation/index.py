from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any


class SirenIndex:
    def __init__(
        self,
        document: Mapping[str, Any],
        excluded_relations: frozenset[str] = frozenset(),
    ):
        self.document = document
        self.properties = set(self.mapping(document.get("properties")))
        self.actions = self.named(document.get("actions"), "name")
        self.relations = {"self"}
        for item in (*self.sequence(document.get("links")), *self.sequence(document.get("entities"))):
            self.relations.update(self.strings(item.get("rel")))
        self.relations -= excluded_relations

    def duplicate_issues(self) -> tuple[dict[str, str], ...]:
        issues = [*self._duplicates(self.actions.keys(), "/actions", "action")]
        for index, action in enumerate(self.sequence(self.document.get("actions"))):
            fields = self.named(action.get("fields"), "name")
            issues.extend(self._duplicates(fields.keys(), f"/actions/{index}/fields", "field"))
        return tuple(issues)

    @staticmethod
    def named(value: Any, field: str) -> dict[str, Mapping[str, Any]]:
        return {
            name: item
            for item in SirenIndex.sequence(value)
            if isinstance((name := item.get(field)), str)
        }

    @staticmethod
    def sequence(value: Any) -> tuple[Mapping[str, Any], ...]:
        if not isinstance(value, (list, tuple)):
            return ()
        return tuple(item for item in value if isinstance(item, Mapping))

    @staticmethod
    def mapping(value: Any) -> Mapping[str, Any]:
        return value if isinstance(value, Mapping) else {}

    @staticmethod
    def strings(value: Any) -> tuple[str, ...]:
        if not isinstance(value, (list, tuple)):
            return ()
        return tuple(item for item in value if isinstance(item, str))

    @staticmethod
    def _duplicates(values: Any, pointer: str, label: str) -> tuple[dict[str, str], ...]:
        counts = Counter(values)
        return tuple(
            {
                "pointer": pointer,
                "message": f"Duplicate Siren {label} identity: {identity!r}",
            }
            for identity, count in sorted(counts.items())
            if count > 1
        )
