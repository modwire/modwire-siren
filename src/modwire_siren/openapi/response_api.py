from copy import deepcopy
from typing import Any

from ..standards import SirenMediaType

SIREN_ENTITY_REF = "#/components/schemas/SirenEntity"
PROBLEM_REF = "#/components/schemas/Problem"


def enrich_siren_openapi(
    schema: dict[str, Any],
    *,
    success_media_type: str = SirenMediaType.ENTITY,
    problem_media_type: str = SirenMediaType.PROBLEM,
) -> dict[str, Any]:
    """Add Siren/problem schemas and rewrite operation response media types."""
    return rewrite_problem_responses(
        rewrite_siren_responses(
            add_siren_components(schema),
            success_media_type=success_media_type,
        ),
        problem_media_type=problem_media_type,
    )


def add_siren_components(schema: dict[str, Any]) -> dict[str, Any]:
    """Add package-owned Siren and problem JSON Schema components."""
    document = deepcopy(schema)
    schemas = document.setdefault("components", {}).setdefault("schemas", {})
    for name, component in _components().items():
        schemas[name] = component
    return document


def rewrite_siren_responses(
    schema: dict[str, Any],
    *,
    success_media_type: str = SirenMediaType.ENTITY,
) -> dict[str, Any]:
    """Rewrite non-204 2xx operation responses to Siren response content."""
    document = deepcopy(schema)
    for response in _responses(document):
        status_code, response_document = response
        if _is_no_content(status_code):
            response_document.pop("content", None)
        elif _is_success(status_code):
            response_document["content"] = _content(success_media_type, SIREN_ENTITY_REF)
    return document


def rewrite_problem_responses(
    schema: dict[str, Any],
    *,
    problem_media_type: str = SirenMediaType.PROBLEM,
) -> dict[str, Any]:
    """Rewrite non-2xx operation responses to problem JSON response content."""
    document = deepcopy(schema)
    for status_code, response in _responses(document):
        if not _is_success(status_code) and not _is_no_content(status_code):
            response["content"] = _content(problem_media_type, PROBLEM_REF)
    return document


def _responses(schema: dict[str, Any]) -> tuple[tuple[str, dict[str, Any]], ...]:
    return tuple(
        (str(status_code), response)
        for path_item in schema.get("paths", {}).values()
        if isinstance(path_item, dict)
        for operation in path_item.values()
        if isinstance(operation, dict)
        for status_code, response in operation.get("responses", {}).items()
        if isinstance(response, dict)
    )


def _is_success(status_code: str) -> bool:
    return status_code.startswith("2") and not _is_no_content(status_code)


def _is_no_content(status_code: str) -> bool:
    return status_code == "204"


def _content(media_type: str, reference: str) -> dict[str, Any]:
    return {
        media_type: {
            "schema": {
                "$ref": reference,
            },
        },
    }


def _components() -> dict[str, dict[str, Any]]:
    return {
        "SirenEntity": {
            "type": "object",
            "properties": {
                "class": {"type": "array", "items": {"type": "string"}},
                "properties": {"type": "object", "additionalProperties": True},
                "entities": {"type": "array", "items": {"$ref": "#/components/schemas/SirenEmbeddedEntity"}},
                "actions": {"type": "array", "items": {"$ref": "#/components/schemas/SirenAction"}},
                "links": {"type": "array", "items": {"$ref": "#/components/schemas/SirenLink"}},
            },
            "additionalProperties": True,
        },
        "SirenEmbeddedEntity": {
            "type": "object",
            "required": ["rel"],
            "properties": {
                "rel": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                "class": {"type": "array", "items": {"type": "string"}},
                "properties": {"type": "object", "additionalProperties": True},
                "entities": {"type": "array", "items": {"$ref": "#/components/schemas/SirenEmbeddedEntity"}},
                "actions": {"type": "array", "items": {"$ref": "#/components/schemas/SirenAction"}},
                "links": {"type": "array", "items": {"$ref": "#/components/schemas/SirenLink"}},
            },
            "additionalProperties": True,
        },
        "SirenAction": {
            "type": "object",
            "required": ["name", "href"],
            "properties": {
                "name": {"type": "string"},
                "href": {"type": "string", "format": "uri-reference"},
                "method": {"type": "string"},
                "title": {"type": "string"},
                "type": {"type": "string"},
                "fields": {"type": "array", "items": {"$ref": "#/components/schemas/SirenField"}},
            },
            "additionalProperties": True,
        },
        "SirenField": {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string"},
                "required": {"type": "boolean"},
                "title": {"type": "string"},
                "value": {},
                "options": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "value": {},
                            "title": {"type": "string"},
                        },
                        "additionalProperties": True,
                    },
                },
                "schema": {"type": "object", "additionalProperties": True},
            },
            "additionalProperties": True,
        },
        "SirenLink": {
            "type": "object",
            "required": ["rel", "href"],
            "properties": {
                "rel": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                "href": {"type": "string", "format": "uri-reference"},
                "title": {"type": "string"},
                "type": {"type": "string"},
            },
            "additionalProperties": True,
        },
        "Problem": {
            "type": "object",
            "required": ["title"],
            "properties": {
                "type": {"type": "string", "format": "uri-reference"},
                "title": {"type": "string"},
                "status": {"type": "integer", "minimum": 100, "maximum": 599},
                "detail": {"type": "string"},
                "instance": {"type": "string", "format": "uri-reference"},
            },
            "additionalProperties": True,
        },
    }


__all__ = [
    "add_siren_components",
    "enrich_siren_openapi",
    "rewrite_problem_responses",
    "rewrite_siren_responses",
]
