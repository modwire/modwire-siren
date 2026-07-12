from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..validation.index import SirenIndex
from ..validation.references import ReferenceValidator
from .standard import ProfileStandard


class ProfileReferences:
    def __init__(self, standard: ProfileStandard):
        self._standard = standard

    def validate(self, metadata: Mapping[str, Any], document: Mapping[str, Any]) -> None:
        index = SirenIndex(document, frozenset({"profile", self._standard.relation}))
        references = ReferenceValidator(index.duplicate_issues())
        properties = metadata["properties"]
        relations = metadata["relations"]
        actions = metadata["actions"]
        result_relations = {
            relation
            for action in actions.values()
            for relation in action["result"]["relations"]
        }
        regions = {
            region["id"]
            for region in metadata["presentation"]["layout"]["regions"]
        }

        references.require(properties, index.properties, "/properties", "property")
        references.require(relations, index.relations | result_relations, "/relations", "relation")
        references.require(actions, set(index.actions), "/actions", "action")

        for action_name in actions.keys() & index.actions.keys():
            action_metadata = actions[action_name]
            action = index.actions[action_name]
            fields = SirenIndex.named(action.get("fields"), "name")
            references.require(
                action_metadata["fields"],
                set(fields),
                f"/actions/{action_name}/fields",
                "field",
            )
            self._action(references, action_name, action_metadata, index.relations, regions)

        for relation_name, relation_metadata in relations.items():
            self._region(references, f"/relations/{relation_name}", relation_metadata, regions)

        for position, region in enumerate(metadata["presentation"]["layout"]["regions"]):
            content = region["content"]
            prefix = f"/presentation/layout/regions/{position}/content"
            references.require(content["properties"], index.properties, f"{prefix}/properties", "property")
            references.require(content["relations"], index.relations, f"{prefix}/relations", "relation")
            references.require(content["actions"], set(index.actions), f"{prefix}/actions", "action")

        references.finish()

    def _action(
        self,
        references: ReferenceValidator,
        action_name: str,
        metadata: Mapping[str, Any],
        relations: set[str],
        regions: set[str],
    ) -> None:
        self._region(references, f"/actions/{action_name}", metadata, regions)
        for field_name, field in metadata["fields"].items():
            choices = field.get("choices", {})
            if choices.get("kind") == "relation":
                references.require_value(
                    choices["relation"],
                    relations,
                    f"/actions/{action_name}/fields/{field_name}/choices/relation",
                    "relation",
                )

    @staticmethod
    def _region(
        references: ReferenceValidator,
        pointer: str,
        metadata: Mapping[str, Any],
        regions: set[str],
    ) -> None:
        if "region" in metadata:
            references.require_value(metadata["region"], regions, f"{pointer}/region", "region")
