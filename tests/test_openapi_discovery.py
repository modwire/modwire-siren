import pytest

from modwire_siren import ModwireSirenFactory, OpenApiError, SirenEntityRequest
from modwire_siren.openapi import discover_resources


SCHEMA = {
    "paths": {
        "/records": {
            "get": {"operationId": "list_records"},
            "post": {"operationId": "create_record"},
        },
        "/records/search": {"get": {"operationId": "search_records"}},
        "/records/{record_id}": {
            "get": {"operationId": "get_record"},
            "patch": {"operationId": "rename_record"},
        },
        "/records/{record_id}/publish": {"post": {"operationId": "publish_record"}},
        "/tags": {"get": {"operationId": "list_tags"}},
    }
}


def test_discovers_resources_and_operations_from_conventional_openapi_paths():
    record, tag = discover_resources(SCHEMA["paths"])

    assert record.name == "record"
    assert record.path == "/records/{record_id}"
    assert record.path_parameters == {"record_id": "id"}
    assert record.operations == ("get_record", "rename_record", "publish_record")
    assert record.collection_operations == ("list_records", "create_record", "search_records")
    assert tag.name == "tag"
    assert tag.collection_only is True


def test_standard_composition_reads_the_openapi_graph_without_siren_extensions():
    siren = ModwireSirenFactory.standard(SCHEMA, "https://api.test")

    document = siren.document(
        SirenEntityRequest(
            resource_name="record",
            properties={"id": "one", "title": "One"},
            operation_ids=("get_record",),
            path_values={"record_id": "one"},
        )
    )

    assert document["links"][0]["href"] == "https://api.test/records/one"


def test_rejects_an_entity_path_that_does_not_follow_the_identifier_contract():
    with pytest.raises(OpenApiError, match="record_id"):
        discover_resources({"/records/{slug}": {"get": {"operationId": "get_record"}}})
