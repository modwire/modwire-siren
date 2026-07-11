from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any

from .error import OpenApiError


class OpenApiSchemaResolver(ABC):
    @abstractmethod
    def resolve(self, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class ComponentSchemaResolver(OpenApiSchemaResolver):
    def __init__(self, components: dict[str, Any]):
        self._components = deepcopy(components)

    def resolve(self, schema: dict[str, Any]) -> dict[str, Any]:
        return self._resolve(schema, ())

    def _resolve(self, schema: dict[str, Any], resolving: tuple[str, ...]) -> dict[str, Any]:
        resolved = deepcopy(schema)
        reference = resolved.pop("$ref", None)
        if reference:
            component_name = reference.rsplit("/", 1)[-1]
            if component_name not in self._components:
                raise OpenApiError(f"Unknown OpenAPI schema reference: {reference}")
            if component_name in resolving:
                chain = " -> ".join((*resolving, component_name))
                raise OpenApiError(f"Circular OpenAPI schema reference: {chain}")
            resolved = deepcopy(self._components[component_name]) | resolved
            resolving = (*resolving, component_name)
        merged: dict[str, Any] = {}
        for part in resolved.pop("allOf", ()):
            merged = self._merge(merged, self._resolve(part, resolving))
        resolved = self._merge(merged, resolved)
        for keyword in ("anyOf", "oneOf", "prefixItems"):
            if keyword in resolved:
                resolved[keyword] = [self._resolve(item, resolving) for item in resolved[keyword]]
        for keyword in ("items", "additionalProperties"):
            if isinstance(resolved.get(keyword), dict):
                resolved[keyword] = self._resolve(resolved[keyword], resolving)
        if "properties" in resolved:
            resolved["properties"] = {
                name: self._resolve(value, resolving) for name, value in resolved["properties"].items()
            }
        return resolved

    @staticmethod
    def _merge(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        merged = left | right
        if "properties" in left or "properties" in right:
            merged["properties"] = left.get("properties", {}) | right.get("properties", {})
        if "required" in left or "required" in right:
            merged["required"] = list(dict.fromkeys((*left.get("required", ()), *right.get("required", ()))))
        return merged
