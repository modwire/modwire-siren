from copy import deepcopy

import pytest

import modwire_siren
from modwire_siren import SirenContext, siren

SCHEMA = {
    "openapi": "3.1.1",
    "info": {"title": "Modwire", "version": "2"},
    "paths": {
        "/records": {
            "get": {"operationId": "list_records", "responses": {"200": {"description": "OK"}}},
        },
        "/records/{record_id}": {
            "parameters": [
                {
                    "name": "record_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "get": {"operationId": "get_record", "responses": {"200": {"description": "OK"}}},
            "patch": {
                "operationId": "rename_record",
                "responses": {"200": {"description": "OK"}},
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["title"],
                                "properties": {"title": {"type": "string"}},
                            }
                        }
                    }
                },
            },
        },
    },
}

REFERENCED_SCHEMA = {
    "openapi": "3.1.1",
    "info": {"title": "Modwire", "version": "2"},
    "paths": {
        "/records": {
            "get": {
                "operationId": "list_records",
                "parameters": [{"$ref": "#/components/parameters/PageSize"}],
                "responses": {"200": {"description": "OK"}},
            }
        },
        "/records/{record_id}": {
            "parameters": [
                {
                    "name": "record_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "patch": {
                "operationId": "rename_record",
                "requestBody": {"$ref": "#/components/requestBodies/RenameRecord"},
                "responses": {"200": {"description": "OK"}},
            },
        },
    },
    "components": {
        "parameters": {
            "PageSize": {
                "name": "page_size",
                "in": "query",
                "required": False,
                "schema": {"$ref": "#/components/schemas/PageSize"},
            }
        },
        "requestBodies": {
            "RenameRecord": {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RenameRecord"}}},
            }
        },
        "schemas": {
            "PageSize": {"type": "integer"},
            "RenameRecord": {
                "type": "object",
                "required": ["title"],
                "properties": {"title": {"$ref": "#/components/schemas/Title", "type": "string"}},
            },
            "Title": {"type": "integer"},
        },
    },
}

ROUTE_POLICY_SCHEMA = {
    "openapi": "3.1.1",
    "info": {"title": "Routes", "version": "1"},
    "paths": {
        "/api/v2/labels": {
            "get": {"operationId": "list_labels", "responses": {"200": {"description": "OK"}}},
            "post": {"operationId": "create_label", "responses": {"201": {"description": "Created"}}},
        },
        "/api/v2/teams/{team}/records": {
            "parameters": [{"name": "team", "in": "path", "required": True, "schema": {"type": "string"}}],
            "get": {"operationId": "list_team_records", "responses": {"200": {"description": "OK"}}},
        },
        "/api/v2/teams/{team}/records/search": {
            "parameters": [{"name": "team", "in": "path", "required": True, "schema": {"type": "string"}}],
            "get": {"operationId": "search_team_records", "responses": {"200": {"description": "OK"}}},
        },
        "/api/v2/teams/{team}/records/{record}": {
            "parameters": [
                {"name": "team", "in": "path", "required": True, "schema": {"type": "string"}},
                {"name": "record", "in": "path", "required": True, "schema": {"type": "string"}},
            ],
            "get": {"operationId": "get_team_record", "responses": {"200": {"description": "OK"}}},
        },
        "/api/v2/teams/{team}/records/{record}/archive": {
            "parameters": [
                {"name": "team", "in": "path", "required": True, "schema": {"type": "string"}},
                {"name": "record", "in": "path", "required": True, "schema": {"type": "string"}},
            ],
            "post": {"operationId": "archive_team_record", "responses": {"204": {"description": "Archived"}}},
        },
        "/api/v2/teams/{team}/records/{record}/reports": {
            "parameters": [
                {"name": "team", "in": "path", "required": True, "schema": {"type": "string"}},
                {"name": "record", "in": "path", "required": True, "schema": {"type": "string"}},
            ],
            "get": {"operationId": "list_record_reports", "responses": {"200": {"description": "OK"}}},
        },
    },
}


def test_public_facade_exports_only_runtime_context_and_siren():
    assert modwire_siren.__all__ == ["SirenContext", "siren"]


def test_public_facade_rejects_an_invalid_openapi_document_and_recovers():
    invalid = deepcopy(REFERENCED_SCHEMA)
    invalid["paths"]["/records/{record_id}"]["parameters"][0]["required"] = False

    with pytest.raises(ValueError, match="OpenAPI document is invalid"):
        siren(invalid)

    document = siren(REFERENCED_SCHEMA).project(
        SirenContext(
            base_url="https://api.example.com",
            scope="collection",
            resource="record",
            capabilities=frozenset({"list_records"}),
        )
    )

    assert document["actions"][0]["fields"] == [{"name": "page_size", "type": "integer", "required": False}]


@pytest.mark.parametrize(
    "reference",
    [
        "#/components/parameters/Missing",
        "#/components/schemas/PageSize",
        "#/components/parameters",
    ],
)
def test_public_facade_rejects_invalid_component_references(reference):
    invalid = deepcopy(REFERENCED_SCHEMA)
    invalid["paths"]["/records"]["get"]["parameters"] = [{"$ref": reference}]

    with pytest.raises(ValueError, match="OpenAPI document is invalid"):
        siren(invalid)


def test_public_facade_rejects_a_cyclic_component_schema():
    cyclic = deepcopy(REFERENCED_SCHEMA)
    cyclic["components"]["schemas"]["Title"] = {"$ref": "#/components/schemas/Title"}

    with pytest.raises(ValueError, match="OpenAPI document is invalid: cyclic reference"):
        siren(cyclic)


def test_public_facade_projects_referenced_request_body_and_schema_siblings():
    document = siren(REFERENCED_SCHEMA).project(
        SirenContext(
            base_url="https://api.example.com",
            resource="record",
            value={"id": "42"},
            capabilities=frozenset({"rename_record"}),
        )
    )

    assert document["actions"][0]["fields"] == [{"name": "title", "type": "string", "required": True}]


def test_public_facade_projects_an_entity_with_concrete_links_and_allowed_actions():
    engine = siren(SCHEMA)

    document = engine.project(
        SirenContext(
            base_url="https://api.example.com",
            resource="record",
            value={"id": "42", "title": "Architecture"},
            capabilities=frozenset({"get_record", "rename_record"}),
        )
    )

    assert document["links"] == [{"rel": ["self"], "href": "https://api.example.com/records/42"}]
    assert [action["name"] for action in document["actions"]] == ["get_record", "rename_record"]
    assert document["actions"][1]["fields"][0] == {"name": "title", "type": "string", "required": True}


def test_engine_rejects_a_capability_outside_the_resource_contract():
    engine = siren(SCHEMA)

    with pytest.raises(ValueError, match="unsupported capabilities"):
        engine.project(
            SirenContext(
                base_url="https://api.example.com",
                resource="record",
                value={"id": "42"},
                capabilities=frozenset({"archive_record"}),
            )
        )


def test_public_facade_uses_an_explicit_mounted_root_path():
    document = siren(SCHEMA, root_path="/siren/").project(
        SirenContext(base_url="https://api.example.com", scope="root")
    )

    assert document["links"][0] == {"rel": ["self"], "href": "https://api.example.com/siren/"}


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
    engine = siren(ROUTE_POLICY_SCHEMA)

    document = engine.project(
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


@pytest.mark.parametrize(
    ("openapi", "root_path", "error", "message"),
    [
        ([], "/", TypeError, "OpenAPI document must be a mapping"),
        (SCHEMA, "siren", ValueError, "Siren root path must start"),
    ],
)
def test_public_facade_rejects_invalid_inputs_before_the_happy_path(openapi, root_path, error, message):
    with pytest.raises(error, match=message):
        siren(openapi, root_path=root_path)
