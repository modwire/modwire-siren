from enum import StrEnum


class SirenMediaType(StrEnum):
    ACTION = "application/json"
    ENTITY = "application/vnd.siren+json"
    PROBLEM = "application/problem+json"


class SirenRelationName(StrEnum):
    SELF = "self"


class SirenFieldType(StrEnum):
    CHECKBOX = "checkbox"
    JSON = "json"
    NUMBER = "number"
    TEXT = "text"


class SirenOpenApiExtension(StrEnum):
    RESOURCE = "x-siren-resource"
    UI_PROFILE = "x-siren-ui-profile"
