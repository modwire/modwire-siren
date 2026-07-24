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
        implemented = self.matches(requirement.schema, actual, capability.schema)
        if requirement.enum_value is not None:
            implemented = implemented and requirement.enum_value in self.enum(actual, capability.schema)
        return SirenFinding(requirement, implemented, "serialized public contract")

    def matches(self, expected: Mapping[str, Any], actual: Mapping[str, Any], document: Mapping[str, Any]) -> bool:
        if "$ref" in actual:
            return self.matches(expected, self.reference(actual["$ref"], document), document)
        if "anyOf" in actual:
            return any(
                self.matches(expected, value, document)
                for value in actual["anyOf"]
                if value.get("type") != "null"
            )
        expected_type = expected.get("type")
        actual_type = actual.get("type")
        expected_types = (expected_type,) if isinstance(expected_type, str) else tuple(expected_type or ())
        actual_types = (actual_type,) if isinstance(actual_type, str) else tuple(actual_type or ())
        types_match = not expected_types or all(
            value in expected_types or (value == "integer" and "number" in expected_types)
            for value in actual_types
        )
        enum_match = "enum" not in expected or set(expected["enum"]).issubset(actual.get("enum", ()))
        default_match = "default" not in expected or actual.get("default") == expected["default"]
        format_match = "format" not in expected or actual.get("format") == expected["format"]
        items_match = "items" not in expected or (
            isinstance(actual.get("items"), Mapping) and self.matches(expected["items"], actual["items"], document)
        )
        minimum_match = "minItems" not in expected or actual.get("minItems", 0) >= expected["minItems"]
        return types_match and enum_match and default_match and format_match and items_match and minimum_match

    def reference(self, reference: str, document: Mapping[str, Any]) -> Mapping[str, Any]:
        value: Any = document
        for segment in reference.removeprefix("#/").split("/"):
            value = value[segment]
        return value

    def enum(self, schema: Mapping[str, Any], document: Mapping[str, Any]) -> tuple[Any, ...]:
        if "$ref" in schema:
            return self.enum(self.reference(schema["$ref"], document), document)
        return tuple(schema.get("enum", ()))
