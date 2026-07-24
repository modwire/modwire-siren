from copy import deepcopy

import pytest
from openapi_documents import SCHEMA

from modwire_siren import SirenCompilationError, SirenContext, SirenProjectionError, siren


class TestErrors:
    def test_public_facade_chains_invalid_openapi_as_a_compilation_error(self):
        with pytest.raises(SirenCompilationError, match="Invalid or unsupported OpenAPI contract") as raised:
            siren([])

        assert isinstance(raised.value.__cause__, TypeError)

    def test_public_facade_chains_unsupported_openapi_mapping_as_a_compilation_error(self):
        invalid = deepcopy(SCHEMA)
        invalid["paths"]["/records/{record_id}"]["patch"]["requestBody"]["content"]["application/json"][
            "schema"
        ]["properties"]["title"] = {"type": "string", "enum": ["draft", "published"]}

        with pytest.raises(SirenCompilationError, match="Invalid or unsupported OpenAPI contract") as raised:
            siren(invalid)

        assert isinstance(raised.value.__cause__, ValueError)

    @pytest.mark.parametrize(
        "context",
        [
            SirenContext(base_url="https://api.example.com", resource="record"),
            SirenContext(base_url="https://api.example.com", resource="unknown"),
            SirenContext(
                base_url="https://api.example.com",
                resource="record",
                value={"id": "42"},
                capabilities=frozenset({"unknown_operation"}),
            ),
        ],
    )
    def test_engine_chains_context_failures_as_projection_errors(self, context):
        with pytest.raises(SirenProjectionError, match="Siren projection failed") as raised:
            siren(SCHEMA).project(context)

        assert isinstance(raised.value.__cause__, ValueError)

    def test_public_facade_recovers_with_compilation_and_projection_success(self):
        document = siren(SCHEMA).project(
            SirenContext(
                base_url="https://api.example.com",
                resource="record",
                value={"id": "42"},
                capabilities=frozenset({"get_record"}),
            )
        )
        document = document.model_dump(by_alias=True, mode="json", exclude_none=True)

        assert document["links"] == [{"rel": ["self"], "href": "https://api.example.com/records/42"}]
