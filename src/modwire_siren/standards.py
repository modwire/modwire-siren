from enum import StrEnum


class SirenMediaType(StrEnum):
    ACTION = "application/json"
    ENTITY = "application/vnd.siren+json"
    OPENAPI = "application/vnd.oai.openapi+json;version=3.1"
    PROBLEM = "application/problem+json"


class SirenRelationName(StrEnum):
    FIRST = "first"
    ITEM = "item"
    NEXT = "next"
    PREVIOUS = "previous"
    SELF = "self"


class SirenFieldType(StrEnum):
    CHECKBOX = "checkbox"
    JSON = "json"
    NUMBER = "number"
    TEXT = "text"


class SirenOpenApiExtension(StrEnum):
    RESOURCE = "x-siren-resource"
    UI_PROFILE = "x-siren-ui-profile"
