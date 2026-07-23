from copy import deepcopy

import pytest
from openapi_documents import REFERENCED_SCHEMA

from modwire_siren import SirenContext, siren


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
    ["#/components/parameters/Missing", "#/components/schemas/PageSize", "#/components/parameters"],
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
