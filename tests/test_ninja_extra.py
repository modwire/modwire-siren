import asyncio
import inspect

import pytest

from modwire_siren import (
    ModwireSirenFactory,
    NinjaExtraSirenController,
    NinjaExtraSirenResponseAdapter,
    SirenEntityDecorator,
    siren_entity,
)

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
        }
    }
}


class RecordController(NinjaExtraSirenController):
    @SirenEntityDecorator("record", operations=("revise_record",))
    def get_record(self, record_slug: str) -> dict:
        return {"slug": record_slug, "title": "Architecture"}

    @siren_entity(resource="record", operations=("revise_record",), headers={"X-Trace-Id": "trace-1"})
    def get_record_response(self, record_slug: str) -> dict:
        return {"slug": record_slug, "title": "Architecture"}

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
