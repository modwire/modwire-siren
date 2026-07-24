from copy import deepcopy

import pytest
from openapi_documents import PARAMETER_MEDIA_SCHEMA

from modwire_siren import SirenCompilationError, SirenContext, siren


class TestFields:
    def test_public_facade_rejects_unsupported_parameter_locations_and_recovers(self):
        invalid = deepcopy(PARAMETER_MEDIA_SCHEMA)
        invalid["paths"]["/records"]["get"]["parameters"].append(
            {"name": "page", "in": "header", "required": False, "schema": {"type": "string"}}
        )

        with pytest.raises(SirenCompilationError, match="Invalid or unsupported OpenAPI contract"):
            siren(invalid)

        assert siren(PARAMETER_MEDIA_SCHEMA).project(
            SirenContext(
                base_url="https://api.example.com",
                scope="collection",
                resource="record",
                capabilities=frozenset({"list_records"}),
            )
        )["actions"][0]["fields"] == [{"name": "page", "type": "text"}]


    def test_public_facade_rejects_a_schema_less_parameter(self):
        invalid = deepcopy(PARAMETER_MEDIA_SCHEMA)
        invalid["paths"]["/records"]["get"]["parameters"] = [
            {"name": "filter", "in": "query", "required": False, "content": {"application/json": {}}}
        ]

        with pytest.raises(SirenCompilationError, match="Invalid or unsupported OpenAPI contract"):
            siren(invalid)


    def test_public_facade_rejects_duplicate_parameter_identities(self):
        invalid = deepcopy(PARAMETER_MEDIA_SCHEMA)
        invalid["paths"]["/records"]["get"]["parameters"] = [
            {"name": "filter", "in": "query", "required": False, "schema": {"type": "string"}},
            {"name": "filter", "in": "query", "required": False, "schema": {"type": "integer"}},
        ]

        with pytest.raises(SirenCompilationError, match="Invalid or unsupported OpenAPI contract"):
            siren(invalid)


    def test_public_facade_prefers_json_request_body_fields(self):
        document = siren(PARAMETER_MEDIA_SCHEMA).project(
            SirenContext(
                base_url="https://api.example.com",
                resource="record",
                value={"id": "42"},
                capabilities=frozenset({"replace_record"}),
            )
        )

        assert document["actions"][0]["fields"] == [{"name": "title", "type": "text"}]


    @pytest.mark.parametrize(
        "content",
        [
            {"text/plain": {"schema": {"type": "string"}}},
            {"text/plain": {"schema": {"type": "string"}}, "application/xml": {"schema": {"type": "string"}}},
        ],
    )
    def test_public_facade_rejects_non_json_request_body_media(self, content):
        invalid = deepcopy(PARAMETER_MEDIA_SCHEMA)
        invalid["paths"]["/records/{record_id}"]["patch"]["requestBody"]["content"] = content

        with pytest.raises(SirenCompilationError, match="Invalid or unsupported OpenAPI contract"):
            siren(invalid)

    @pytest.mark.parametrize(
        ("parameter", "message"),
        [
            (
                {"name": "page", "in": "query", "required": True, "schema": {"type": "integer"}},
                "OpenAPI required query parameter is unsupported: page",
            ),
            (
                {"name": "session", "in": "cookie", "required": False, "schema": {"type": "string"}},
                "OpenAPI parameter location is unsupported: cookie",
            ),
        ],
    )
    def test_public_facade_rejects_unrepresentable_parameter_controls(self, parameter, message):
        invalid = deepcopy(PARAMETER_MEDIA_SCHEMA)
        invalid["paths"]["/records"]["get"]["parameters"] = [parameter]

        with pytest.raises(SirenCompilationError, match="Invalid or unsupported OpenAPI contract"):
            siren(invalid)

    @pytest.mark.parametrize(
        "schema",
        [
            {"type": "array", "items": {"type": "string"}},
            {"type": "object"},
            {"type": "null"},
            {"type": "string", "enum": ["draft", "published"]},
            {"oneOf": [{"type": "string"}, {"type": "integer"}]},
            {"type": "string", "format": "uuid"},
        ],
    )
    def test_public_facade_rejects_unmappable_field_schemas(self, schema):
        invalid = deepcopy(PARAMETER_MEDIA_SCHEMA)
        invalid["paths"]["/records"]["get"]["parameters"] = [
            {"name": "value", "in": "query", "required": False, "schema": schema}
        ]

        with pytest.raises(SirenCompilationError, match="Invalid or unsupported OpenAPI contract"):
            siren(invalid)

    def test_public_facade_rejects_required_json_body_controls(self):
        invalid = deepcopy(PARAMETER_MEDIA_SCHEMA)
        invalid["paths"]["/records/{record_id}"]["patch"]["requestBody"]["content"]["application/json"][
            "schema"
        ]["required"] = ["title"]

        with pytest.raises(SirenCompilationError, match="Invalid or unsupported OpenAPI contract"):
            siren(invalid)

    @pytest.mark.parametrize("method", ["head", "options"])
    def test_public_facade_rejects_unsupported_http_methods(self, method):
        invalid = deepcopy(PARAMETER_MEDIA_SCHEMA)
        invalid["paths"]["/records"][method] = {
            "operationId": f"{method}_records",
            "responses": {"200": {"description": "OK"}},
        }

        with pytest.raises(SirenCompilationError, match="Invalid or unsupported OpenAPI contract"):
            siren(invalid)

    def test_public_facade_maps_supported_query_and_json_body_fields(self):
        document = deepcopy(PARAMETER_MEDIA_SCHEMA)
        document["paths"]["/records"]["parameters"] = []
        document["paths"]["/records"]["get"]["parameters"] = [
            {"name": "text", "in": "query", "required": False, "schema": {"type": "string"}},
            {"name": "email", "in": "query", "required": False, "schema": {"type": "string", "format": "email"}},
            {"name": "uri", "in": "query", "required": False, "schema": {"type": "string", "format": "uri"}},
            {"name": "date", "in": "query", "required": False, "schema": {"type": "string", "format": "date"}},
            {
                "name": "date_time",
                "in": "query",
                "required": False,
                "schema": {"type": "string", "format": "date-time"},
            },
            {"name": "time", "in": "query", "required": False, "schema": {"type": "string", "format": "time"}},
            {"name": "integer", "in": "query", "required": False, "schema": {"type": "integer"}},
            {"name": "number", "in": "query", "required": False, "schema": {"type": "number"}},
            {"name": "boolean", "in": "query", "required": False, "schema": {"type": "boolean"}},
        ]
        document["paths"]["/records/{record_id}"]["patch"]["requestBody"]["content"]["application/json"][
            "schema"
        ]["properties"] = {
            "title": {"type": "string"},
            "priority": {"type": "integer"},
            "published": {"type": "boolean"},
        }
        engine = siren(document)

        collection = engine.project(
            SirenContext(
                base_url="https://api.example.com",
                scope="collection",
                resource="record",
                capabilities=frozenset({"list_records"}),
            )
        )
        entity = engine.project(
            SirenContext(
                base_url="https://api.example.com",
                resource="record",
                value={"id": "42"},
                capabilities=frozenset({"replace_record"}),
            )
        )

        assert collection["actions"][0]["fields"] == [
            {"name": "text", "type": "text"},
            {"name": "email", "type": "email"},
            {"name": "uri", "type": "url"},
            {"name": "date", "type": "date"},
            {"name": "date_time", "type": "datetime-local"},
            {"name": "time", "type": "time"},
            {"name": "integer", "type": "number"},
            {"name": "number", "type": "number"},
            {"name": "boolean", "type": "checkbox"},
        ]
        assert entity["actions"][0]["fields"] == [
            {"name": "title", "type": "text"},
            {"name": "priority", "type": "number"},
            {"name": "published", "type": "checkbox"},
        ]
