import pytest

import modwire_siren
from modwire_siren import SirenContext, siren

SCHEMA = {
    "info": {"title": "Modwire", "version": "2"},
    "paths": {
        "/records": {
            "get": {"operationId": "list_records"},
        },
        "/records/{record_id}": {
            "get": {"operationId": "get_record"},
            "patch": {
                "operationId": "rename_record",
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


def test_public_facade_exports_only_runtime_context_and_siren():
    assert modwire_siren.__all__ == ["SirenContext", "siren"]


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
