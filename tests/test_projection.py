import pytest
from openapi_documents import SCHEMA

from modwire_siren import SirenContext, siren


def test_public_facade_projects_an_entity_with_concrete_links_and_allowed_actions():
    document = siren(SCHEMA).project(
        SirenContext(
            base_url="https://api.example.com",
            resource="record",
            value={"id": "42", "title": "Architecture"},
            capabilities=frozenset({"get_record", "rename_record"}),
        )
    )

    assert document["links"] == [{"rel": ["self"], "href": "https://api.example.com/records/42"}]
    assert [action["name"] for action in document["actions"]] == ["get_record", "rename_record"]
    assert document["actions"][0] == {
        "name": "get_record",
        "href": "https://api.example.com/records/42",
        "method": "GET",
    }
    assert document["actions"][1]["type"] == "application/json"
    assert document["actions"][1]["fields"][0] == {"name": "title", "type": "string", "required": True}


def test_engine_rejects_a_capability_outside_the_resource_contract():
    with pytest.raises(ValueError, match="unsupported capabilities"):
        siren(SCHEMA).project(
            SirenContext(
                base_url="https://api.example.com",
                resource="record",
                value={"id": "42"},
                capabilities=frozenset({"archive_record"}),
            )
        )


def test_public_facade_projects_only_followable_root_links_and_eligible_root_actions():
    schema = {
        "openapi": "3.1.1",
        "info": {"title": "Root actions", "version": "1"},
        "paths": {
            "/records": {"get": {"operationId": "list_records", "responses": {"200": {"description": "OK"}}}},
            "/searches": {
                "get": {
                    "operationId": "search_records",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["phrase"],
                                    "properties": {"phrase": {"type": "string"}},
                                }
                            }
                        }
                    },
                    "responses": {"200": {"description": "OK"}},
                }
            },
            "/outboxes": {"post": {"operationId": "clear_outbox", "responses": {"204": {"description": "OK"}}}},
            "/commands/rebuild": {
                "post": {
                    "operationId": "rebuild_index",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["scope"],
                                    "properties": {"scope": {"type": "string"}},
                                }
                            }
                        }
                    },
                    "responses": {"202": {"description": "Accepted"}},
                }
            },
            "/records/{record_id}": {
                "parameters": [
                    {"name": "record_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "get": {"operationId": "get_record", "responses": {"200": {"description": "OK"}}},
            },
            "/commands/{command_id}/run": {
                "parameters": [
                    {"name": "command_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "post": {"operationId": "run_command", "responses": {"202": {"description": "Accepted"}}},
            },
        },
    }

    document = siren(schema).project(
        SirenContext(
            base_url="https://api.example.com",
            scope="root",
            query=(("format", "siren"),),
            capabilities=frozenset({"search_records", "rebuild_index", "get_record", "run_command"}),
        )
    )

    assert document["links"] == [
        {"rel": ["self"], "href": "https://api.example.com/?format=siren"},
        {"rel": ["record"], "href": "https://api.example.com/records"},
    ]
    assert document["actions"] == [
        {
            "name": "search_records",
            "href": "https://api.example.com/searches",
            "method": "GET",
            "type": "application/json",
            "fields": [{"name": "phrase", "type": "string", "required": True}],
        },
        {
            "name": "rebuild_index",
            "href": "https://api.example.com/commands/rebuild",
            "method": "POST",
            "type": "application/json",
            "fields": [{"name": "scope", "type": "string", "required": True}],
        },
    ]
