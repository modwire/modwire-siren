from enum import StrEnum


class OpenApiHttpMethod(StrEnum):
    DELETE = "delete"
    GET = "get"
    HEAD = "head"
    OPTIONS = "options"
    PATCH = "patch"
    POST = "post"
    PUT = "put"
    TRACE = "trace"
