import sys
import types

import pytest

from modwire_siren.integrations.django import (
    django_problem_response,
    django_validation_problem_response,
    to_django_response,
)
from modwire_siren.integrations.ninja_extra.response import NinjaExtraSirenResponse
from modwire_siren.standards import SirenMediaType


class FakeHttpResponse:
    def __init__(self, content: str | bytes = b"", *, status: int = 200, content_type: str | None = None):
        self.status_code = status
        self.content = content.encode() if isinstance(content, str) else content
        self.headers = {"Content-Type": "text/html; charset=utf-8" if content_type is None else content_type}

    def __setitem__(self, name: str, value: str) -> None:
        self.headers[name] = value

    def __delitem__(self, name: str) -> None:
        del self.headers[name]


class HttpError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


@pytest.fixture
def django_http(monkeypatch):
    django_module = types.ModuleType("django")
    http_module = types.ModuleType("django.http")
    http_module.HttpResponse = FakeHttpResponse
    monkeypatch.setitem(sys.modules, "django", django_module)
    monkeypatch.setitem(sys.modules, "django.http", http_module)


def test_to_django_response_maps_siren_body_status_content_type_and_headers(django_http):
    response = to_django_response(
        NinjaExtraSirenResponse(
            {"class": ["record"], "properties": {"slug": "architecture"}},
            status_code=201,
            headers={"Location": "/records/architecture", "Content-Length": "999"},
            content_type=SirenMediaType.ENTITY,
        )
    )

    assert response.status_code == 201
    assert response.content == b'{"class":["record"],"properties":{"slug":"architecture"}}'
    assert response.headers == {
        "Content-Type": "application/vnd.siren+json",
        "Location": "/records/architecture",
    }


def test_to_django_response_maps_problem_json(django_http):
    response = to_django_response(
        NinjaExtraSirenResponse(
            {"title": "Missing record", "status": 404},
            status_code=404,
            content_type=SirenMediaType.PROBLEM,
        )
    )

    assert response.status_code == 404
    assert response.content == b'{"title":"Missing record","status":404}'
    assert response.headers["Content-Type"] == "application/problem+json"


def test_to_django_response_maps_no_content_without_content_type(django_http):
    response = to_django_response(
        NinjaExtraSirenResponse(
            None,
            status_code=204,
            headers={"X-Trace-Id": "trace-1"},
            content_type=None,
        )
    )

    assert response.status_code == 204
    assert response.content == b""
    assert response.headers == {"X-Trace-Id": "trace-1"}


def test_to_django_response_rejects_content_type_headers(django_http):
    with pytest.raises(ValueError, match="content_type"):
        to_django_response(
            NinjaExtraSirenResponse(
                {"title": "Conflict"},
                status_code=409,
                headers={"Content-Type": "text/plain"},
                content_type=SirenMediaType.PROBLEM,
            )
        )


def test_to_django_response_rejects_none_body_for_content_responses(django_http):
    with pytest.raises(ValueError, match="204 No Content"):
        to_django_response(NinjaExtraSirenResponse(None, status_code=200, content_type=None))


def test_to_django_response_rejects_missing_content_type_for_body(django_http):
    with pytest.raises(ValueError, match="content_type"):
        to_django_response(NinjaExtraSirenResponse({"ok": True}, content_type=None))


def test_django_problem_response_maps_framework_exception_to_problem_payload():
    response = django_problem_response(HttpError(404, "Missing record"))

    assert response.status_code == 404
    assert response.content_type == "application/problem+json"
    assert response.body == {
        "title": "Not found",
        "status": 404,
        "detail": "Missing record",
    }


def test_django_validation_problem_response_maps_validation_details():
    response = django_validation_problem_response({"title": "Missing title"}, status=400)

    assert response.status_code == 400
    assert response.content_type == "application/problem+json"
    assert response.body == {
        "title": "Validation error",
        "status": 400,
        "errors": ({"field": "title", "message": "Missing title"},),
    }
