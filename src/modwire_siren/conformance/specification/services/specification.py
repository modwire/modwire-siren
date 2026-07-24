import json
from collections.abc import Mapping
from dataclasses import dataclass
from importlib.resources import files
from typing import Any

from wireup import injectable

from ..contracts import SirenSpecification
from ..values import SirenRequirement


@injectable(as_type=SirenSpecification)
@dataclass(frozen=True)
class SirenSchemaSpecification(SirenSpecification):
    def requirements(self) -> tuple[SirenRequirement, ...]:
        document = json.loads(files("modwire_siren.runtime.document.schema").joinpath("siren.schema.json").read_text())
        definitions = (("Entity", document), *document["definitions"].items())
        requirements: tuple[SirenRequirement, ...] = ()
        for name, definition in definitions:
            effective = self.effective(definition, document)
            for member, member_schema in effective.get("properties", {}).items():
                requirement = SirenRequirement(name, member, member_schema, member in effective.get("required", []))
                requirements += (requirement,)
                for value in member_schema.get("enum", []):
                    requirements += (SirenRequirement(name, member, member_schema, requirement.required, value),)
        return requirements

    def effective(self, schema: Mapping[str, Any], document: Mapping[str, Any]) -> dict[str, Any]:
        if "$ref" in schema:
            return self.effective(self.reference(schema["$ref"], document), document)
        effective = dict(schema)
        properties: dict[str, Any] = {}
        required: list[str] = []
        for member in schema.get("allOf", []):
            incoming = self.effective(member, document)
            properties.update(incoming.get("properties", {}))
            required.extend(incoming.get("required", []))
        properties.update(schema.get("properties", {}))
        required.extend(schema.get("required", []))
        if properties:
            effective["properties"] = properties
        if required:
            effective["required"] = list(dict.fromkeys(required))
        return effective

    def reference(self, reference: str, document: Mapping[str, Any]) -> Mapping[str, Any]:
        if reference == "#":
            return document
        value: Any = document
        for segment in reference.removeprefix("#/").split("/"):
            value = value[segment]
        if not isinstance(value, Mapping):
            raise ValueError(f"Siren schema reference does not resolve to an object: {reference}")
        return value
