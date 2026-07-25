from copy import deepcopy

import pytest
from openapi_documents import ROUTE_POLICY_SCHEMA, SCHEMA

from modwire_siren import SirenCompilationError, SirenContext, SirenProjectionError, siren


class TestRoutes:
    def test_public_facade_derives_prefixed_collection_nested_and_entity_route_ownership(self):
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
        collection = collection.model_dump(by_alias=True, mode="json", exclude_none=True)
        entity = entity.model_dump(by_alias=True, mode="json", exclude_none=True)

        assert collection["links"] == [
            {"rel": ["self"], "href": "https://api.example.com/api/v2/teams/north%2Feast/records"}
        ]
        assert [action["name"] for action in collection["actions"]] == ["list_team_records", "search_team_records"]
        assert entity["links"] == [
            {"rel": ["self"], "href": "https://api.example.com/api/v2/teams/north%2Feast/records/r%2F42"}
        ]
        assert [action["name"] for action in entity["actions"]] == ["get_team_record", "archive_team_record"]


    def test_public_facade_uses_plural_static_subpaths_as_nested_resource_ownership(self):
        document = siren(ROUTE_POLICY_SCHEMA).project(
            SirenContext(
                base_url="https://api.example.com",
                scope="collection",
                resource="report",
                path_values={"team": "team", "record": "record"},
                capabilities=frozenset({"list_record_reports"}),
            )
        )
        document = document.model_dump(by_alias=True, mode="json", exclude_none=True)

        assert document["links"] == [
            {"rel": ["self"], "href": "https://api.example.com/api/v2/teams/team/records/record/reports"}
        ]
        assert [action["name"] for action in document["actions"]] == ["list_record_reports"]


    def test_public_facade_ignores_standalone_static_command_endpoints_without_losing_resource_actions(self):
        schema = deepcopy(SCHEMA)
        schema["paths"].update(
            {
                "/scaffoldings/converge": {
                    "post": {"operationId": "converge_scaffoldings", "responses": {"200": {"description": "OK"}}}
                },
                "/scaffoldings/{scaffolding_id}/schema": {
                    "parameters": [
                        {
                            "name": "scaffolding_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "get": {"operationId": "get_scaffolding_schema", "responses": {"200": {"description": "OK"}}},
                },
                "/scaffoldings/{scaffolding_id}/bundle": {
                    "parameters": [
                        {
                            "name": "scaffolding_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "post": {"operationId": "bundle_scaffolding", "responses": {"200": {"description": "OK"}}},
                },
                "/scaffoldings/{scaffolding_id}/preview": {
                    "parameters": [
                        {
                            "name": "scaffolding_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "get": {"operationId": "preview_scaffolding", "responses": {"200": {"description": "OK"}}},
                },
            }
        )

        document = siren(schema).project(
            SirenContext(
                base_url="https://api.example.com",
                scope="collection",
                resource="record",
                capabilities=frozenset({"list_records"}),
            )
        )
        document = document.model_dump(by_alias=True, mode="json", exclude_none=True)

        assert document["actions"] == [
            {"name": "list_records", "href": "https://api.example.com/records", "method": "GET"}
        ]


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
    def test_public_facade_rejects_unowned_routes_and_recovers(self, path, parameters, message):
        invalid = deepcopy(SCHEMA)
        invalid["paths"] = {
            path: {
                "parameters": parameters,
                "get": {"operationId": "unknown", "responses": {"200": {"description": "OK"}}},
            }
        }

        with pytest.raises(SirenCompilationError, match="Invalid or unsupported OpenAPI contract"):
            siren(invalid)

        document = siren(ROUTE_POLICY_SCHEMA).project(
            SirenContext(base_url="https://api.example.com", scope="collection", resource="label")
        )
        assert document.model_dump(by_alias=True, mode="json", exclude_none=True)["links"] == [
            {"rel": ["self"], "href": "https://api.example.com/api/v2/labels"}
        ]


    def test_public_facade_rejects_indistinguishable_duplicate_resources_and_missing_path_values(self):
        invalid = deepcopy(ROUTE_POLICY_SCHEMA)
        invalid["paths"]["/api/v2/archives/{team}/records"] = {
            "parameters": [{"name": "team", "in": "path", "required": True, "schema": {"type": "string"}}],
            "get": {"operationId": "list_archived_records", "responses": {"200": {"description": "OK"}}},
        }

        with pytest.raises(SirenCompilationError, match="Invalid or unsupported OpenAPI contract"):
            siren(invalid)
        with pytest.raises(SirenProjectionError, match="Siren projection failed"):
            siren(ROUTE_POLICY_SCHEMA).project(
                SirenContext(base_url="https://api.example.com", scope="collection", resource="record")
            )


    def test_public_facade_selects_nested_duplicate_resources_from_parent_path_values_after_ambiguity(self):
        schema = deepcopy(SCHEMA)
        schema["paths"]["/sections/{section_id}/records"] = {
            "parameters": [{"name": "section_id", "in": "path", "required": True, "schema": {"type": "string"}}],
            "get": {"operationId": "list_section_records", "responses": {"200": {"description": "OK"}}},
        }
        schema["paths"]["/authors/{author_id}/records"] = {
            "parameters": [{"name": "author_id", "in": "path", "required": True, "schema": {"type": "string"}}],
            "get": {"operationId": "list_author_records", "responses": {"200": {"description": "OK"}}},
        }
        engine = siren(schema)

        with pytest.raises(SirenProjectionError, match="Siren projection failed"):
            engine.project(
                SirenContext(
                    base_url="https://api.example.com",
                    scope="collection",
                    resource="record",
                    path_values={"section_id": "section", "author_id": "author"},
                )
            )

        document = engine.project(
            SirenContext(
                base_url="https://api.example.com",
                scope="collection",
                resource="record",
                path_values={"section_id": "section"},
                capabilities=frozenset({"list_section_records"}),
            )
        )
        document = document.model_dump(by_alias=True, mode="json", exclude_none=True)

        assert document["links"] == [{"rel": ["self"], "href": "https://api.example.com/sections/section/records"}]
        assert [action["name"] for action in document["actions"]] == ["list_section_records"]


    def test_public_facade_ignores_trailing_slash_mounted_root_route(self):
        schema = deepcopy(SCHEMA)
        schema["paths"]["/api/"] = {"get": {"responses": {"200": {"description": "OK"}}}}
        engine = siren(schema, root_path="/api/")

        document = engine.project(SirenContext(base_url="https://api.example.com", scope="root"))
        assert document.model_dump(by_alias=True, mode="json", exclude_none=True)["links"] == [
            {"rel": ["self"], "href": "https://api.example.com/api/"},
            {"rel": ["collection"], "href": "https://api.example.com/records"},
        ]


    def test_public_facade_rejects_path_item_references_and_trace_operations_without_losing_operations(self):
        referenced = deepcopy(SCHEMA)
        referenced["paths"]["/records"] = {"$ref": "#/components/pathItems/Records"}
        referenced["components"] = {
            "pathItems": {
                "Records": {"get": {"operationId": "list_records", "responses": {"200": {"description": "OK"}}}}
            }
        }

        with pytest.raises(SirenCompilationError, match="Invalid or unsupported OpenAPI contract"):
            siren(referenced)

        traced = deepcopy(SCHEMA)
        traced["paths"]["/records"]["trace"] = {
            "operationId": "trace_records",
            "responses": {"200": {"description": "OK"}},
        }

        with pytest.raises(SirenCompilationError, match="Invalid or unsupported OpenAPI contract"):
            siren(traced)

        document = siren(SCHEMA).project(
            SirenContext(
                base_url="https://api.example.com",
                scope="collection",
                resource="record",
                capabilities=frozenset({"list_records"}),
            )
        )
        assert document.model_dump(by_alias=True, mode="json", exclude_none=True)["actions"] == [
            {"name": "list_records", "href": "https://api.example.com/records", "method": "GET"}
        ]
