import json
from contextlib import suppress

from .ninja_extra.problem import exception_problem_response, problem_from_exception, validation_problem_response
from .ninja_extra.response import NinjaExtraSirenResponse

CONTENT_LENGTH = "content-length"
CONTENT_TYPE = "content-type"


def to_django_response(response: NinjaExtraSirenResponse):
    if any(name.lower() == CONTENT_TYPE for name in response.headers):
        raise ValueError("Pass response media type through content_type, not headers")
    try:
        from django.http import HttpResponse
    except ImportError as error:
        raise ImportError("Django is required; install modwire-siren[django] to use this adapter") from error

    if response.body is None:
        if response.status_code != 204:
            raise ValueError("Response body can only be None for 204 No Content")
        django_response = HttpResponse(status=response.status_code)
        _delete_header(django_response, "Content-Type")
        _delete_header(django_response, "Content-Length")
    else:
        if response.content_type is None:
            raise ValueError("Response content_type is required when body is present")
        body = json.dumps(response.body, ensure_ascii=False, separators=(",", ":"))
        django_response = HttpResponse(body, status=response.status_code, content_type=response.content_type)

    for name, value in response.headers.items():
        if name.lower() == CONTENT_LENGTH:
            continue
        django_response[name] = value
    return django_response


def _delete_header(response, name: str) -> None:
    with suppress(KeyError):
        del response[name]


def django_problem_response(error: BaseException, **kwargs) -> NinjaExtraSirenResponse:
    return exception_problem_response(error, **kwargs)


def django_validation_problem_response(errors, **kwargs) -> NinjaExtraSirenResponse:
    return validation_problem_response(errors, **kwargs)


__all__ = [
    "django_problem_response",
    "django_validation_problem_response",
    "problem_from_exception",
    "to_django_response",
]
