from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from wireup import injectable

from ...implementation.values import SirenCapability
from ...specification.values import SirenRequirement
from ..contracts import SirenRequirementMatcher
from ..values import SirenConformanceReport, SirenFinding


@injectable(as_type=SirenRequirementMatcher)
@dataclass(frozen=True)
class SirenDefaultRequirementMatcher(SirenRequirementMatcher):
    def match(
        self, requirements: tuple[SirenRequirement, ...], capabilities: tuple[SirenCapability, ...]
    ) -> SirenConformanceReport:
        capability_by_definition = {capability.definition: capability for capability in capabilities}
        findings = tuple(
            self.finding(requirement, capability_by_definition.get(requirement.definition))
            for requirement in requirements
        )
        return SirenConformanceReport(findings)

    def finding(self, requirement: SirenRequirement, capability: SirenCapability | None) -> SirenFinding:
        if capability is None:
            return SirenFinding(requirement, False, "no public representation")
        properties = capability.schema.get("properties", {})
        actual = properties.get(requirement.member) if isinstance(properties, Mapping) else None
        if not isinstance(actual, Mapping):
            return SirenFinding(requirement, False, "member is absent")
        required = capability.schema.get("required", ())
        if requirement.required and requirement.member not in required:
            return SirenFinding(requirement, False, "required member is optional")
        implemented = self.matches(requirement.schema, actual, requirement.document, capability.schema)
        if requirement.enum_value is not None:
            implemented = implemented and requirement.enum_value in self.enum(actual, capability.schema)
        return SirenFinding(requirement, implemented, "serialized public contract")

    def matches(
        self,
        expected: Mapping[str, Any],
        actual: Mapping[str, Any],
        expected_document: Mapping[str, Any],
        actual_document: Mapping[str, Any],
    ) -> bool:
        self.validate(expected)
        if "$ref" in expected:
            return self.matches(
                self.reference(expected["$ref"], expected_document), actual, expected_document, actual_document
            )
        if "$ref" in actual:
            return self.matches(
                expected,
                {
                    **self.reference(actual["$ref"], actual_document),
                    **{key: value for key, value in actual.items() if key != "$ref"},
                },
                expected_document,
                actual_document,
            )
        if "allOf" in actual:
            return all(self.matches(expected, value, expected_document, actual_document) for value in actual["allOf"])
        if "anyOf" in actual:
            return all(
                self.matches(expected, value, expected_document, actual_document)
                for value in actual["anyOf"]
                if value.get("type") != "null"
            )
        if "oneOf" in actual:
            return all(
                self.matches(expected, value, expected_document, actual_document) for value in actual["oneOf"]
            )
        if "allOf" in expected:
            return all(self.matches(value, actual, expected_document, actual_document) for value in expected["allOf"])
        if "anyOf" in expected or "oneOf" in expected:
            alternatives = expected.get("anyOf", expected.get("oneOf", ()))
            return any(self.matches(value, actual, expected_document, actual_document) for value in alternatives)
        expected_type = expected.get("type")
        actual_type = actual.get("type")
        expected_types = (expected_type,) if isinstance(expected_type, str) else tuple(expected_type or ())
        actual_types = (actual_type,) if isinstance(actual_type, str) else tuple(actual_type or ())
        types_match = not expected_types or (bool(actual_types) and all(
            value in expected_types or (value == "integer" and "number" in expected_types)
            for value in actual_types
        ))
        enum_match = "enum" not in expected or set(expected["enum"]).issubset(actual.get("enum", ()))
        default_match = "default" not in expected or actual.get("default") == expected["default"]
        format_match = "format" not in expected or actual.get("format") == expected["format"]
        pattern_match = "pattern" not in expected or actual.get("pattern") == expected["pattern"]
        items_match = "items" not in expected or (
            isinstance(actual.get("items"), Mapping)
            and self.matches(expected["items"], actual["items"], expected_document, actual_document)
        )
        minimum_match = "minItems" not in expected or actual.get("minItems", 0) >= expected["minItems"]
        return all((types_match, enum_match, default_match, format_match, pattern_match, items_match, minimum_match))

    def reference(self, reference: str, document: Mapping[str, Any]) -> Mapping[str, Any]:
        if reference == "#":
            return document
        value: Any = document
        for segment in reference.removeprefix("#/").split("/"):
            value = value[segment]
        if not isinstance(value, Mapping):
            raise ValueError(f"Siren schema reference does not resolve to an object: {reference}")
        return value

    def validate(self, schema: Mapping[str, Any]) -> None:
        supported = {
            "$ref",
            "$schema",
            "allOf",
            "anyOf",
            "default",
            "definitions",
            "description",
            "enum",
            "format",
            "id",
            "items",
            "minItems",
            "oneOf",
            "pattern",
            "properties",
            "required",
            "title",
            "type",
        }
        unsupported = set(schema).difference(supported)
        if unsupported:
            terms = ", ".join(sorted(unsupported))
            raise ValueError(f"Unsupported Siren schema terms: {terms}")

    def enum(self, schema: Mapping[str, Any], document: Mapping[str, Any]) -> tuple[Any, ...]:
        if "$ref" in schema:
            return self.enum(self.reference(schema["$ref"], document), document)
        return tuple(schema.get("enum", ()))
