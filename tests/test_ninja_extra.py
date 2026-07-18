import asyncio
import inspect
from dataclasses import dataclass
from typing import Any

import pytest

from modwire_siren import (
    ModwireSirenFactory,
    NinjaExtraSirenController,
    NinjaExtraSirenResponseAdapter,
    SirenEntityDecorator,
    SirenEntityRequest,
    siren_entity,
)
from modwire_siren.integrations.ninja_extra import problem_from_exception, validation_problem


@dataclass(frozen=True, slots=True)
class RecordData:
    slug: str
    title: str


class RecordModel:
    def __init__(self, slug: str, title: str):
        self.slug = slug
        self.title = title

    def model_dump(self) -> dict[str, str]:
        return {"slug": self.slug, "title": self.title}


class RecordOrm:
    def __init__(self, slug: str, title: str):
        self.slug = slug
        self.title = title


class OrmSerializer:
    def serialize(self, value: Any) -> dict[str, str]:
        if not isinstance(value, RecordOrm):
            raise TypeError(f"Unsupported ORM value: {type(value).__name__}")
        return {"slug": value.slug, "title": value.title}


class Request:
    def __init__(self, origin: str):
        self.origin = origin

    def build_absolute_uri(self, path: str) -> str:
        return f"{self.origin.rstrip('/')}/{path.lstrip('/')}"


class HttpError(Exception):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code


class ValidationError(Exception):
    def errors(self) -> list[dict[str, str]]:
        return [{"field": "title", "message": "Missing title"}]


SCHEMA = {
    "paths": {
        "/records/{record_slug}": {
            "x-siren-resource": {
                "name": "record",
                "class": "record",
                "identifier": "slug",
                "path-parameters": {"record_slug": "slug"},
                "relations": {},
            },
            "get": {"operationId": "get_record"},
            "patch": {"operationId": "revise_record"},
        },
        "/records/search": {
            "x-siren-resource": {
                "name": "record_search",
                "class": "record-search",
                "identifier": "",
                "path-parameters": {},
                "relations": {},
                "operations": ("search_records",),
                "singleton": True,
            },
            "post": {"operationId": "search_records"},
        },
        "/records/{record_slug}/schema": {
            "x-siren-resource": {
                "name": "record_schema",
                "class": "record-schema",
                "identifier": "",
                "path-parameters": {"record_slug": "record_slug"},
                "relations": {},
                "operations": ("get_record_schema",),
                "singleton": True,
            },
            "get": {"operationId": "get_record_schema"},
        }
    }
}


class RecordController(NinjaExtraSirenController):
    @SirenEntityDecorator("record", operations=("revise_record",))
    def get_record(self, record_slug: str) -> dict:
        return {"slug": record_slug, "title": "Architecture"}

    @SirenEntityDecorator("record", operations=("revise_record",))
    def get_record_document_from_dataclass(self, record_slug: str) -> RecordData:
        return RecordData(slug=record_slug, title="Architecture")

    @siren_entity(resource="record", operations=("revise_record",), headers={"X-Trace-Id": "trace-1"})
    def get_record_response(self, record_slug: str) -> dict:
        return {"slug": record_slug, "title": "Architecture"}

    @siren_entity(resource="record", operations=("revise_record",))
    def get_record_response_from_model(self, record_slug: str) -> RecordModel:
        return RecordModel(slug=record_slug, title="Architecture")

    @siren_entity(resource="record", operations=("revise_record",), serializer=OrmSerializer())
    def get_record_response_from_orm(self, record_slug: str) -> RecordOrm:
        return RecordOrm(slug=record_slug, title="Architecture")

    @SirenEntityDecorator("record", operations=())
    async def get_record_async(self, record_slug: str) -> dict:
        return {"slug": record_slug}

    @siren_entity(resource="record", operations=())
    async def get_record_response_async(self, record_slug: str) -> dict:
        return {"slug": record_slug}

    @siren_entity(resource="record", operations=(), status_code=204)
    def delete_record(self, record_slug: str) -> None:
        return None


def controller() -> RecordController:
    return RecordController(ModwireSirenFactory.standard(SCHEMA, "https://api.test"))


def test_siren_entity_keeps_controller_thin_and_preserves_route_signature():
    assert str(inspect.signature(RecordController.get_record)) == "(self, record_slug: str) -> dict"

    document = controller().get_record("architecture/aggregate")

    assert document["properties"] == {"slug": "architecture/aggregate", "title": "Architecture"}
    assert document["links"][0]["href"] == "https://api.test/records/architecture%2Faggregate"
    assert [action["name"] for action in document["actions"]] == ["revise_record"]


def test_siren_entity_document_serializes_dataclass_returns_before_projection():
    document = controller().get_record_document_from_dataclass("architecture")

    assert document["properties"] == {"slug": "architecture", "title": "Architecture"}
    assert document["links"][0]["href"] == "https://api.test/records/architecture"


def test_siren_entity_supports_async_controller_methods():
    document = asyncio.run(controller().get_record_async("architecture"))
    assert document["class"] == ["record"]


def test_siren_entity_response_sets_siren_content_type_and_preserves_headers():
    assert str(inspect.signature(RecordController.get_record_response)) == "(self, record_slug: str) -> dict"

    response = controller().get_record_response("architecture/aggregate")

    assert response.status_code == 200
    assert response.content_type == "application/vnd.siren+json"
    assert response.headers == {"X-Trace-Id": "trace-1"}
    assert response.body["properties"] == {"slug": "architecture/aggregate", "title": "Architecture"}
    assert response.body["links"][0]["href"] == "https://api.test/records/architecture%2Faggregate"
    assert [action["name"] for action in response.body["actions"]] == ["revise_record"]


def test_siren_entity_response_serializes_model_dump_returns_before_projection():
    response = controller().get_record_response_from_model("architecture")

    assert response.body["properties"] == {"slug": "architecture", "title": "Architecture"}
    assert response.body["links"][0]["href"] == "https://api.test/records/architecture"


def test_siren_entity_response_uses_decorator_serializer_for_orm_returns():
    response = controller().get_record_response_from_orm("architecture")

    assert response.body["properties"] == {"slug": "architecture", "title": "Architecture"}


def test_siren_entity_response_supports_async_controller_methods():
    response = asyncio.run(controller().get_record_response_async("architecture"))
    assert response.body["class"] == ["record"]


def test_siren_entity_response_handles_no_content_status_cleanly():
    response = controller().delete_record("architecture")

    assert response.status_code == 204
    assert response.body is None
    assert response.content_type is None


def test_response_adapter_projects_entities_without_controller_subclassing():
    adapter = NinjaExtraSirenResponseAdapter(ModwireSirenFactory.standard(SCHEMA, "https://api.test"))

    response = adapter.entity(
        "record",
        {"slug": "architecture"},
        operations=(),
        status_code=201,
        headers={"Location": "/records/architecture"},
    )

    assert response.status_code == 201
    assert response.content_type == "application/vnd.siren+json"
    assert response.headers == {"Location": "/records/architecture"}
    assert response.body["links"][0]["href"] == "https://api.test/records/architecture"


def test_response_adapter_serializes_properties_with_adapter_serializer():
    adapter = NinjaExtraSirenResponseAdapter(
        ModwireSirenFactory.standard(SCHEMA, "https://api.test"),
        property_serializer=OrmSerializer(),
    )

    response = adapter.entity(
        "record",
        RecordOrm("architecture", "Architecture"),
        operations=(),
    )

    assert response.body["properties"] == {"slug": "architecture", "title": "Architecture"}


def test_response_adapter_for_request_uses_request_base_url_resolver():
    siren_factory = ModwireSirenFactory.web(
        SCHEMA,
        base_url_resolver=lambda request: request.build_absolute_uri("/api/"),
    )
    adapter = NinjaExtraSirenResponseAdapter.for_request(
        siren_factory=siren_factory,
        request=Request("https://tenant.test"),
    )

    response = adapter.entity("record", {"slug": "architecture"}, operations=())

    assert response.body["links"][0]["href"] == "https://tenant.test/api/records/architecture"


def test_response_adapter_projects_static_singleton_entity_with_self_link():
    adapter = NinjaExtraSirenResponseAdapter(ModwireSirenFactory.standard(SCHEMA, "https://api.test"))

    response = adapter.entity(
        "record_search",
        {"results": []},
        operations=("search_records",),
    )

    assert response.body["class"] == ["record-search"]
    assert response.body["links"][0]["href"] == "https://api.test/records/search"
    assert [action["name"] for action in response.body["actions"]] == ["search_records"]


def test_response_adapter_projects_singleton_subresource_from_path_values():
    adapter = NinjaExtraSirenResponseAdapter(ModwireSirenFactory.standard(SCHEMA, "https://api.test"))

    response = adapter.entity(
        "record_schema",
        {"fields": []},
        operations=("get_record_schema",),
        path_values={"record_slug": "architecture"},
    )

    assert response.body["class"] == ["record-schema"]
    assert response.body["links"][0]["href"] == "https://api.test/records/architecture/schema"


def test_web_factory_accepts_static_base_url_resolver():
    siren = ModwireSirenFactory.web(SCHEMA, base_url_resolver="https://static.test/api/").for_request(object())

    document = siren.document(
        SirenEntityRequest(
            resource_name="record",
            properties={"slug": "architecture"},
            operation_ids=(),
            path_values={},
            entities=(),
        )
    )

    assert document["links"][0]["href"] == "https://static.test/api/records/architecture"


def test_controller_for_request_uses_request_base_url_resolver():
    siren_factory = ModwireSirenFactory.web(
        SCHEMA,
        base_url_resolver=lambda request: request.build_absolute_uri("/api/"),
    )
    controller = RecordController.for_request(
        siren_factory=siren_factory,
        request=Request("https://preview.test"),
    )

    response = controller.get_record_response("architecture")

    assert response.body["links"][0]["href"] == "https://preview.test/api/records/architecture"


def test_response_adapter_reports_clear_property_serialization_failures():
    adapter = NinjaExtraSirenResponseAdapter(ModwireSirenFactory.standard(SCHEMA, "https://api.test"))

    with pytest.raises(TypeError, match="Siren property serialization requires"):
        adapter.entity("record", object(), operations=())


def test_response_adapter_builds_problem_json_responses():
    adapter = NinjaExtraSirenResponseAdapter(ModwireSirenFactory.standard(SCHEMA, "https://api.test"))

    response = adapter.problem(
        {"title": "Missing record", "status": 404},
        status_code=404,
        headers={"X-Trace-Id": "trace-1"},
    )

    assert response.status_code == 404
    assert response.content_type == "application/problem+json"
    assert response.headers == {"X-Trace-Id": "trace-1"}
    assert response.body == {"title": "Missing record", "status": 404}


def test_response_adapter_adds_response_status_to_problem_documents():
    adapter = NinjaExtraSirenResponseAdapter(ModwireSirenFactory.standard(SCHEMA, "https://api.test"))

    response = adapter.problem({"title": "Conflict"}, status_code=409)

    assert response.status_code == 409
    assert response.body == {"status": 409, "title": "Conflict"}


def test_problem_from_exception_preserves_http_status_and_detail():
    problem = problem_from_exception(HttpError(404, "Record not found"))

    assert problem == {
        "title": "Not found",
        "status": 404,
        "detail": "Record not found",
    }


def test_validation_problem_preserves_error_details():
    problem = validation_problem({"title": "Missing title"}, detail="Invalid input")

    assert problem == {
        "title": "Validation error",
        "status": 422,
        "detail": "Invalid input",
        "errors": ({"field": "title", "message": "Missing title"},),
    }


def test_response_adapter_builds_problem_from_exception():
    adapter = NinjaExtraSirenResponseAdapter(ModwireSirenFactory.standard(SCHEMA, "https://api.test"))

    response = adapter.exception(HttpError(403, "No access"), headers={"X-Trace-Id": "trace-1"})

    assert response.status_code == 403
    assert response.content_type == "application/problem+json"
    assert response.headers == {"X-Trace-Id": "trace-1"}
    assert response.body == {"title": "Forbidden", "status": 403, "detail": "No access"}


def test_response_adapter_builds_problem_from_validation_error():
    adapter = NinjaExtraSirenResponseAdapter(ModwireSirenFactory.standard(SCHEMA, "https://api.test"))

    response = adapter.exception(ValidationError(), status=422)

    assert response.status_code == 422
    assert response.body == {
        "title": "Validation error",
        "status": 422,
        "errors": ({"field": "title", "message": "Missing title"},),
    }


def test_response_adapter_builds_validation_problem_response():
    adapter = NinjaExtraSirenResponseAdapter(ModwireSirenFactory.standard(SCHEMA, "https://api.test"))

    response = adapter.validation([{"field": "slug", "message": "Invalid slug"}], status=400)

    assert response.status_code == 400
    assert response.body == {
        "title": "Validation error",
        "status": 400,
        "errors": ({"field": "slug", "message": "Invalid slug"},),
    }


def test_response_adapter_rejects_content_type_header_duplication():
    adapter = NinjaExtraSirenResponseAdapter(ModwireSirenFactory.standard(SCHEMA, "https://api.test"))

    with pytest.raises(ValueError, match="content_type"):
        adapter.entity("record", {"slug": "architecture"}, operations=(), headers={"Content-Type": "text/plain"})


def test_response_adapter_rejects_mismatched_problem_status():
    adapter = NinjaExtraSirenResponseAdapter(ModwireSirenFactory.standard(SCHEMA, "https://api.test"))

    with pytest.raises(ValueError, match="must match"):
        adapter.problem({"title": "Missing record", "status": 400}, status_code=404)


def test_siren_entity_response_rejects_no_content_body():
    class InvalidController(NinjaExtraSirenController):
        @siren_entity(resource="record", operations=(), status_code=204)
        def delete_record(self, record_slug: str) -> dict:
            return {"slug": record_slug}

    with pytest.raises(ValueError, match="must not include a body"):
        InvalidController(ModwireSirenFactory.standard(SCHEMA, "https://api.test")).delete_record("architecture")


def test_siren_entity_rejects_blank_resource_names_at_declaration_time():
    with pytest.raises(ValueError, match="must not be blank"):
        SirenEntityDecorator(" ", operations=())
