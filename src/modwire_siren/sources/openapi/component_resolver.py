from copy import deepcopy
from typing import Any


class ComponentResolver:
    def __init__(self, components: Any) -> None:
        self.components = components if isinstance(components, dict) else {}

    def parameter(self, definition: Any) -> dict[str, Any]:
        return self.resolve(definition, "parameters")

    def request_body(self, definition: Any) -> dict[str, Any]:
        return self.resolve(definition, "requestBodies")

    def schema(self, definition: Any) -> dict[str, Any]:
        return self.resolve(definition, "schemas")

    def resolve(self, definition: Any, kind: str, trail: tuple[str, ...] = ()) -> dict[str, Any]:
        if not isinstance(definition, dict):
            return {}
        result = deepcopy(definition)
        reference = result.pop("$ref", None)
        if reference is None:
            return result
        if not isinstance(reference, str):
            raise ValueError("OpenAPI component reference must be a string")
        if reference in trail:
            raise ValueError(f"OpenAPI component reference cycle: {' -> '.join((*trail, reference))}")
        component_kind, name = self.address(reference, kind)
        collection = self.components.get(component_kind)
        target = collection.get(name) if isinstance(collection, dict) else None
        if not isinstance(target, dict):
            raise ValueError(f"OpenAPI component reference is unknown: {reference}")
        return self.resolve(target, kind, (*trail, reference)) | result

    def address(self, reference: str, expected_kind: str) -> tuple[str, str]:
        prefix = "#/components/"
        if not reference.startswith(prefix):
            raise ValueError(f"OpenAPI component reference is unsupported: {reference}")
        parts = reference[len(prefix) :].split("/")
        if len(parts) != 2:
            raise ValueError(f"OpenAPI component reference is invalid: {reference}")
        kind, encoded_name = parts
        if kind != expected_kind:
            raise ValueError(
                f"OpenAPI component reference {reference!r} must target components/{expected_kind}, "
                f"not components/{kind}"
            )
        return kind, self.decode(encoded_name, reference)

    def decode(self, token: str, reference: str) -> str:
        decoded = ""
        index = 0
        while index < len(token):
            character = token[index]
            if character != "~":
                decoded += character
                index += 1
                continue
            if index + 1 == len(token) or token[index + 1] not in {"0", "1"}:
                raise ValueError(f"OpenAPI component reference is invalid: {reference}")
            decoded += "~" if token[index + 1] == "0" else "/"
            index += 2
        return decoded
