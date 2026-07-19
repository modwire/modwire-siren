import pytest

from modwire_siren import SirenApiService, SirenContext
from modwire_siren.builder import SirenBuilderService
from modwire_siren.extras import siren
from modwire_siren.sources import OpenApiSource, SirenSource

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


def test_openapi_source_compiles_the_api_graph():
    api = SirenApiService((OpenApiSource(),)).build(SCHEMA)

    assert api.root.title == "Modwire"
    assert api.resources[0].entity_operations == ("get_record", "rename_record")
    assert api.operations[2].fields[0].name == "title"


def test_extra_projects_an_entity_with_concrete_links_and_allowed_actions():
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


class RecordsSource(SirenSource):
    def load(self, schema):
        return (
            SirenBuilderService()
            .add_resource("record", "record", "/records", "/records/{record_id}")
            .add_operation("record", "collection", "list_records", "GET", "/records")
            .build()
        )


class RenameSource(SirenSource):
    def load(self, schema):
        return (
            SirenBuilderService()
            .add_resource("record", "record", "/records", "/records/{record_id}")
            .add_operation("record", "entity", "rename_record", "PATCH", "/records/{record_id}")
            .build()
        )


def test_service_merges_compatible_source_contributions():
    api = SirenApiService((RecordsSource(), RenameSource())).build({})

    assert api.resources[0].collection_operations == ("list_records",)
    assert api.resources[0].entity_operations == ("rename_record",)
