from __future__ import annotations

import json
from collections.abc import Mapping
from copy import deepcopy
from importlib.resources import files
from typing import Any

from jsonschema import Draft202012Validator

from ..error import SirenError
from .pointer import JsonPointer


class JsonSchema:
    def __init__(self, package: str, resource: str):
        schema_path = files(package).joinpath(resource)
        self.document = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(self.document)
        self._validator = Draft202012Validator(self.document)

    def normalize(self, value: Mapping[str, Any]) -> dict[str, Any]:
        raw = self._json(value)
        normalized = deepcopy(raw)
        self._defaults(normalized, self.document)
        self._validate(normalized)
        return normalized

    def validate(self, value: Mapping[str, Any]) -> dict[str, Any]:
        raw = self._json(value)
        self._validate(raw)
        return raw

    def _json(self, value: Mapping[str, Any]) -> dict[str, Any]:
        try:
            return json.loads(json.dumps(dict(value)))
        except (TypeError, ValueError) as error:
            raise SirenError(
                "schema.invalid",
                "Value must be JSON-compatible",
                issues=({"pointer": "", "message": str(error)},),
            ) from error

    def _validate(self, value: dict[str, Any]) -> None:
        issues = tuple(
            {
                "pointer": JsonPointer.from_path(error.absolute_path),
                "message": error.message,
            }
            for error in sorted(
                self._validator.iter_errors(value),
                key=lambda item: tuple(map(str, item.absolute_path)),
            )
        )
        if issues:
            raise SirenError("schema.invalid", "Value does not satisfy its JSON Schema", issues=issues)

    def _defaults(self, value: Any, schema: Any) -> None:
        if not isinstance(schema, dict):
            return
        schema = self._resolved(schema)
        if isinstance(value, dict):
            properties = schema.get("properties", {})
            for name, definition in properties.items():
                if not isinstance(definition, dict):
                    continue
                resolved = self._resolved(definition)
                if name not in value and "default" in resolved:
                    value[name] = deepcopy(resolved["default"])
                if name in value:
                    self._defaults(value[name], definition)
            additional = schema.get("additionalProperties")
            if isinstance(additional, dict):
                for name in value.keys() - properties.keys():
                    self._defaults(value[name], additional)
        elif isinstance(value, list) and isinstance(schema.get("items"), dict):
            for item in value:
                self._defaults(item, schema["items"])

    def _resolved(self, schema: dict[str, Any]) -> dict[str, Any]:
        reference = schema.get("$ref")
        if not isinstance(reference, str) or not reference.startswith("#/"):
            return schema
        target: Any = self.document
        for part in reference[2:].split("/"):
            target = target[part.replace("~1", "/").replace("~0", "~")]
        return {**target, **{name: value for name, value in schema.items() if name != "$ref"}}
