from copy import deepcopy

import pytest
from openapi_documents import ROUTE_POLICY_SCHEMA, SCHEMA

from modwire_siren import SirenContext, siren


def test_public_facade_derives_prefixed_collection_nested_and_entity_route_ownership():
    engine = siren(ROUTE_POLICY_SCHEMA)
    collection = engine.project(
        SirenContext(
            base_url="https://api.example.com",
            scope="collection",
            resource="record",
            path_values={"team": "north/east"},
            capabilities=frozenset({"list_team_records", "search_team_records"}),
        )
    )
    entity = engine.project(
        SirenContext(
            base_url="https://api.example.com",
            resource="record",
            value={"id": "r/42"},
            path_values={"team": "north/east"},
            capabilities=frozenset({"get_team_record", "archive_team_record"}),
        )
    )

    assert collection["links"] == [
        {"rel": ["self"], "href": "https://api.example.com/api/v2/teams/north%2Feast/records"}
    ]
    assert [action["name"] for action in collection["actions"]] == ["list_team_records", "search_team_records"]
    assert entity["links"] == [
        {"rel": ["self"], "href": "https://api.example.com/api/v2/teams/north%2Feast/records/r%2F42"}
    ]
    assert [action["name"] for action in entity["actions"]] == ["get_team_record", "archive_team_record"]


def test_public_facade_uses_plural_static_subpaths_as_nested_resource_ownership():
    document = siren(ROUTE_POLICY_SCHEMA).project(
        SirenContext(
            base_url="https://api.example.com",
            scope="collection",
            resource="report",
            path_values={"team": "team", "record": "record"},
            capabilities=frozenset({"list_record_reports"}),
        )
    )

    assert document["links"] == [
        {"rel": ["self"], "href": "https://api.example.com/api/v2/teams/team/records/record/reports"}
    ]
    assert [action["name"] for action in document["actions"]] == ["list_record_reports"]


@pytest.mark.parametrize(
    ("path", "parameters", "message"),
    [
        ("/", [], "OpenAPI route is unsupported"),
        (
            "/records/{record}/archive/{token}",
            [
                {"name": "record", "in": "path", "required": True, "schema": {"type": "string"}},
                {"name": "token", "in": "path", "required": True, "schema": {"type": "string"}},
            ],
            "OpenAPI route is unsupported",
        ),
    ],
)
def test_public_facade_rejects_unowned_routes_and_recovers(path, parameters, message):
    invalid = deepcopy(SCHEMA)
    invalid["paths"] = {
        path: {
            "parameters": parameters,
            "get": {"operationId": "unknown", "responses": {"200": {"description": "OK"}}},
        }
    }

    with pytest.raises(ValueError, match=message):
        siren(invalid)

    assert siren(ROUTE_POLICY_SCHEMA).project(
        SirenContext(base_url="https://api.example.com", scope="collection", resource="label")
    )["links"] == [{"rel": ["self"], "href": "https://api.example.com/api/v2/labels"}]


def test_public_facade_rejects_duplicate_derived_resources_and_missing_path_values():
    invalid = deepcopy(ROUTE_POLICY_SCHEMA)
    invalid["paths"]["/api/v2/archives/records"] = {
        "get": {"operationId": "list_archived_records", "responses": {"200": {"description": "OK"}}}
    }

    with pytest.raises(ValueError, match="duplicate resource 'record'"):
        siren(invalid)
    with pytest.raises(ValueError, match="Siren link requires path value: team"):
        siren(ROUTE_POLICY_SCHEMA).project(
            SirenContext(base_url="https://api.example.com", scope="collection", resource="record")
        )
