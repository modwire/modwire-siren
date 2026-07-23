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
