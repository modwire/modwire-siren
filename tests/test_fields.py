from copy import deepcopy

import pytest
from openapi_documents import PARAMETER_MEDIA_SCHEMA

from modwire_siren import SirenContext, siren


class TestFields:
    def test_public_facade_rejects_unsupported_parameter_locations_and_recovers(self):
        invalid = deepcopy(PARAMETER_MEDIA_SCHEMA)
        invalid["paths"]["/records"]["get"]["parameters"].append(
            {"name": "page", "in": "header", "required": False, "schema": {"type": "string"}}
        )

        with pytest.raises(ValueError, match="OpenAPI parameter location is unsupported: header"):
            siren(invalid)

        assert siren(PARAMETER_MEDIA_SCHEMA).project(
            SirenContext(
                base_url="https://api.example.com",
                scope="collection",
                resource="record",
                capabilities=frozenset({"list_records"}),
            )
        )["actions"][0]["fields"] == [{"name": "page", "type": "string", "required": True}]


    def test_public_facade_rejects_a_schema_less_parameter(self):
        invalid = deepcopy(PARAMETER_MEDIA_SCHEMA)
        invalid["paths"]["/records"]["get"]["parameters"] = [
            {"name": "filter", "in": "query", "required": False, "content": {"application/json": {}}}
        ]

        with pytest.raises(ValueError, match="OpenAPI parameter schema is required: filter"):
            siren(invalid)


    def test_public_facade_rejects_duplicate_parameter_identities(self):
        invalid = deepcopy(PARAMETER_MEDIA_SCHEMA)
        invalid["paths"]["/records"]["get"]["parameters"] = [
            {"name": "filter", "in": "query", "required": False, "schema": {"type": "string"}},
            {"name": "filter", "in": "query", "required": False, "schema": {"type": "integer"}},
        ]

        with pytest.raises(ValueError, match="OpenAPI document is invalid"):
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

        assert document["actions"][0]["fields"] == [{"name": "title", "type": "string", "required": True}]


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

        with pytest.raises(ValueError, match="OpenAPI request body must provide application/json"):
            siren(invalid)
