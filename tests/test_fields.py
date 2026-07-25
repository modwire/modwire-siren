from copy import deepcopy

import pytest
from openapi_documents import PARAMETER_MEDIA_SCHEMA

from modwire_siren import ModwireSirenError, SirenContext, siren


class TestFields:
    def test_public_facade_delegates_header_and_cookie_parameters(self):
        document = deepcopy(PARAMETER_MEDIA_SCHEMA)
        document["paths"]["/records"]["get"]["parameters"].extend([
            {"name": "trace", "in": "header", "schema": {"type": "string"}},
            {"name": "session", "in": "cookie", "schema": {"type": "string"}},
        ])

        document = siren(document).project(
            SirenContext(
                base_url="https://api.example.com",
                scope="collection",
                resource="record",
                capabilities=frozenset({"list_records"}),
            )
        )
        assert document.model_dump(by_alias=True, mode="json", exclude_none=True)["actions"][0]["fields"] == [
            {"name": "page", "type": "text"}
        ]


    def test_public_facade_rejects_a_schema_less_parameter(self):
        invalid = deepcopy(PARAMETER_MEDIA_SCHEMA)
        invalid["paths"]["/records"]["get"]["parameters"] = [
            {"name": "filter", "in": "query", "required": False, "content": {"application/json": {}}}
        ]

        with pytest.raises(ModwireSirenError, match="Invalid or unsupported OpenAPI contract"):
            siren(invalid)


    def test_public_facade_rejects_duplicate_parameter_identities(self):
        invalid = deepcopy(PARAMETER_MEDIA_SCHEMA)
        invalid["paths"]["/records"]["get"]["parameters"] = [
            {"name": "filter", "in": "query", "required": False, "schema": {"type": "string"}},
            {"name": "filter", "in": "query", "required": False, "schema": {"type": "integer"}},
        ]

        with pytest.raises(ModwireSirenError, match="Invalid or unsupported OpenAPI contract"):
            siren(invalid)


    def test_public_facade_rejects_ambiguous_non_json_request_body_media(self):
        invalid = deepcopy(PARAMETER_MEDIA_SCHEMA)
        invalid["paths"]["/records/{record_id}"]["patch"]["requestBody"]["content"] = {
            "text/plain": {"schema": {"type": "string"}},
            "application/xml": {"schema": {"type": "string"}},
        }

        with pytest.raises(ModwireSirenError, match="Invalid or unsupported OpenAPI contract"):
            siren(invalid)

    @pytest.mark.parametrize(
        "schema",
        [
            {"type": "null"},
            {"oneOf": [{"type": "string"}, {"type": "integer"}]},
        ],
    )
    def test_public_facade_rejects_unmappable_field_schemas(self, schema):
        invalid = deepcopy(PARAMETER_MEDIA_SCHEMA)
        invalid["paths"]["/records"]["get"]["parameters"] = [
            {"name": "value", "in": "query", "required": False, "schema": schema}
        ]

        with pytest.raises(ModwireSirenError, match="Invalid or unsupported OpenAPI contract"):
            siren(invalid)

    def test_public_facade_delegates_structured_inputs_and_non_json_bodies(self):
        document = deepcopy(PARAMETER_MEDIA_SCHEMA)
        document["paths"]["/records"]["parameters"] = []
        document["paths"]["/records"]["get"]["parameters"] = [
            {"name": "page", "in": "query", "schema": {"type": "integer"}},
            {"name": "filter", "in": "query", "schema": {"$ref": "#/components/schemas/Filter"}},
            {"name": "matrix", "in": "query", "schema": {"$ref": "#/components/schemas/Matrix"}},
            {"name": "trace", "in": "header", "schema": {"type": "string"}},
            {"name": "session", "in": "cookie", "schema": {"type": "string"}},
        ]
        document["components"] = {"schemas": {
            "Filter": {"type": "object", "additionalProperties": {"type": "string"}},
            "Matrix": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
            "Metadata": {"type": "object", "properties": {"source": {"type": "string"}}},
        }}
        body = document["paths"]["/records/{record_id}"]["patch"]["requestBody"]["content"][
            "application/json"
        ]["schema"]
        body["properties"] = {
            "title": {"type": "string"},
            "metadata": {"$ref": "#/components/schemas/Metadata"},
            "items": {"type": "array", "items": {"$ref": "#/components/schemas/Metadata"}},
        }

        engine = siren(document)
        collection = engine.project(SirenContext(
            base_url="https://api.example.com",
            scope="collection",
            resource="record",
            capabilities=frozenset({"list_records"}),
        )).model_dump(by_alias=True, mode="json", exclude_none=True)
        entity = engine.project(SirenContext(
            base_url="https://api.example.com",
            resource="record",
            value={"id": "42"},
            capabilities=frozenset({"replace_record"}),
        )).model_dump(by_alias=True, mode="json", exclude_none=True)

        assert collection["actions"][0]["fields"] == [{"name": "page", "type": "number"}]
        assert entity["actions"][0]["fields"] == [{"name": "title", "type": "text"}]

        document["paths"]["/records/{record_id}"]["patch"]["requestBody"]["content"] = {"text/plain": {}}
        delegated = siren(document).project(SirenContext(
            base_url="https://api.example.com",
            resource="record",
            value={"id": "42"},
            capabilities=frozenset({"replace_record"}),
        )).model_dump(by_alias=True, mode="json", exclude_none=True)

        assert delegated["actions"][0] == {
            "name": "replace_record",
            "href": "https://api.example.com/records/42",
            "method": "PATCH",
            "type": "text/plain",
        }

    def test_public_facade_projects_common_openapi_controls(self):
        document = deepcopy(PARAMETER_MEDIA_SCHEMA)
        document["paths"]["/records"]["parameters"] = []
        document["paths"]["/records"]["get"]["parameters"] = [
            {"name": "request_id", "in": "query", "required": True, "schema": {"type": "string", "format": "uuid"}},
            {"name": "tags", "in": "query", "schema": {"type": "array", "items": {"type": "string"}}},
            {"name": "status", "in": "query", "schema": {"type": "string", "enum": ["draft", "published"]}},
            {
                "name": "scopes",
                "in": "query",
                "schema": {"type": "array", "items": {"type": "string", "enum": ["read", "write"]}},
            },
            {"name": "nickname", "in": "query", "schema": {"type": ["string", "null"]}},
            {
                "name": "external_id",
                "in": "query",
                "schema": {"oneOf": [{"type": "string", "format": "uuid"}, {"type": "null"}]},
            },
            {
                "name": "reference",
                "in": "query",
                "schema": {"allOf": [{"type": "string"}, {"format": "uuid"}]},
            },
        ]
        body = document["paths"]["/records/{record_id}"]["patch"]["requestBody"]["content"][
            "application/json"
        ]["schema"]
        body["required"] = ["title"]
        body["properties"] = {
            "title": {"type": "string"},
            "visibility": {"type": "string", "enum": ["private", "public"]},
        }

        engine = siren(document)
        collection = engine.project(
            SirenContext(
                base_url="https://api.example.com",
                scope="collection",
                resource="record",
                capabilities=frozenset({"list_records"}),
            )
        ).model_dump(by_alias=True, mode="json", exclude_none=True)
        entity = engine.project(
            SirenContext(
                base_url="https://api.example.com",
                resource="record",
                value={"id": "42"},
                capabilities=frozenset({"replace_record"}),
            )
        ).model_dump(by_alias=True, mode="json", exclude_none=True)

        assert collection["actions"][0]["fields"] == [
            {"name": "request_id", "type": "text"},
            {"name": "tags", "type": "text"},
            {
                "name": "status",
                "type": "radio",
                "value": [{"value": "draft", "selected": False}, {"value": "published", "selected": False}],
            },
            {
                "name": "scopes",
                "type": "checkbox",
                "value": [{"value": "read", "selected": False}, {"value": "write", "selected": False}],
            },
            {"name": "nickname", "type": "text"},
            {"name": "external_id", "type": "text"},
            {"name": "reference", "type": "text"},
        ]
        assert entity["actions"][0]["fields"] == [
            {"name": "title", "type": "text"},
            {
                "name": "visibility",
                "type": "radio",
                "value": [{"value": "private", "selected": False}, {"value": "public", "selected": False}],
            },
        ]

    @pytest.mark.parametrize("method", ["head", "options"])
    def test_public_facade_rejects_unsupported_http_methods(self, method):
        invalid = deepcopy(PARAMETER_MEDIA_SCHEMA)
        invalid["paths"]["/records"][method] = {
            "operationId": f"{method}_records",
            "responses": {"200": {"description": "OK"}},
        }

        with pytest.raises(ModwireSirenError, match="Invalid or unsupported OpenAPI contract"):
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
        document = document.model_dump(by_alias=True, mode="json", exclude_none=True)

        assert document["actions"][0]["fields"] == [{"name": "title", "type": "text"}]

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
        collection = collection.model_dump(by_alias=True, mode="json", exclude_none=True)
        entity = entity.model_dump(by_alias=True, mode="json", exclude_none=True)

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
