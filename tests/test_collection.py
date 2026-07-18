import pytest

from modwire_siren import (
    CustomPagination,
    ModwireSirenFactory,
    NinjaExtraSirenResponseAdapter,
    OffsetPagination,
    OpenApiError,
    PaginationLinkInput,
    SirenCollectionRequest,
)

SCHEMA = {
    "openapi": "3.1.0",
    "paths": {
        "/records": {
            "get": {
                "operationId": "list_records",
                "summary": "List records",
                "parameters": [
                    {"in": "query", "name": "limit", "required": False, "schema": {"type": "integer"}},
                    {"in": "query", "name": "offset", "required": False, "schema": {"type": "integer"}},
                ],
            },
            "post": {
                "operationId": "create_record",
                "summary": "Create record",
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
        "/records/{record_slug}": {
            "x-siren-resource": {
                "name": "record",
                "class": "record",
                "identifier": "slug",
                "path-parameters": {"record_slug": "slug"},
                "relations": {},
            },
            "get": {"operationId": "get_record", "summary": "Get record"},
            "patch": {"operationId": "revise_record", "summary": "Revise record"},
        },
    },
}


def siren():
    return ModwireSirenFactory.standard(SCHEMA, "https://api.test/")


def test_collection_projects_items_links_actions_and_offset_pagination():
    document = siren().collection(
        SirenCollectionRequest(
            resource_name="record",
            items=(
                {"slug": "architecture/aggregate", "title": "Architecture"},
                {"slug": "billing", "title": "Billing"},
            ),
            collection_operation_ids=("list_records", "create_record"),
            item_operation_ids=("get_record",),
            path_values={},
            pagination=OffsetPagination(limit=50, offset=50, count=125, has_next=True),
        )
    )

    assert document["class"] == ["collection", "record"]
    assert document["properties"] == {"count": 125}
    assert [link["rel"] for link in document["links"]] == [["self"], ["first"], ["previous"], ["next"]]
    assert document["links"][0]["href"] == "https://api.test/records?limit=50&offset=50"
    assert document["links"][1]["href"] == "https://api.test/records?limit=50&offset=0"
    assert document["links"][2]["href"] == "https://api.test/records?limit=50&offset=0"
    assert document["links"][3]["href"] == "https://api.test/records?limit=50&offset=100"
    assert [action["name"] for action in document["actions"]] == ["list_records", "create_record"]
    assert [entity["rel"] for entity in document["entities"]] == [["item"], ["item"]]
    assert document["entities"][0]["properties"] == {"slug": "architecture/aggregate", "title": "Architecture"}
    assert document["entities"][0]["links"][0]["href"] == "https://api.test/records/architecture%2Faggregate"
    assert [action["name"] for action in document["entities"][0]["actions"]] == ["get_record"]


def test_collection_defaults_to_current_item_count_and_self_link_without_pagination():
    document = siren().collection(
        SirenCollectionRequest(
            resource_name="record",
            items=({"slug": "architecture"},),
            collection_operation_ids=("list_records",),
            item_operation_ids=(),
            path_values={},
        )
    )

    assert document["properties"] == {"count": 1}
    assert document["links"][0]["rel"] == ["self"]
    assert document["links"][0]["href"] == "https://api.test/records"


def test_collection_supports_custom_pagination_links():
    document = siren().collection(
        SirenCollectionRequest(
            resource_name="record",
            items=(),
            collection_operation_ids=("list_records",),
            item_operation_ids=(),
            path_values={},
            pagination=CustomPagination(
                count=500,
                links=(
                    PaginationLinkInput(rel="self", query={"cursor": "abc"}),
                    PaginationLinkInput(rel="next", query={"cursor": "def"}),
                ),
            ),
        )
    )

    assert document["properties"] == {"count": 500}
    assert document["links"] == [
        {
            "rel": ["self"],
            "href": "https://api.test/records?cursor=abc",
            "title": "self",
            "type": "application/vnd.siren+json",
        },
        {
            "rel": ["next"],
            "href": "https://api.test/records?cursor=def",
            "title": "next",
            "type": "application/vnd.siren+json",
        }
    ]


def test_collection_requires_custom_pagination_self_link():
    with pytest.raises(ValueError, match="self link"):
        siren().collection(
            SirenCollectionRequest(
                resource_name="record",
                items=(),
                collection_operation_ids=("list_records",),
                item_operation_ids=(),
                path_values={},
                pagination=CustomPagination(
                    count=500,
                    links=(PaginationLinkInput(rel="next", query={"cursor": "def"}),),
                ),
            )
        )


def test_collection_rejects_missing_collection_operation_source():
    with pytest.raises(OpenApiError, match="at least one collection operation"):
        siren().collection(
            SirenCollectionRequest(
                resource_name="record",
                items=(),
                collection_operation_ids=(),
                item_operation_ids=(),
                path_values={},
            )
        )


def test_collection_rejects_mismatched_collection_operation_paths():
    with pytest.raises(OpenApiError, match="do not share path"):
        siren().collection(
            SirenCollectionRequest(
                resource_name="record",
                items=(),
                collection_operation_ids=("list_records", "get_record"),
                item_operation_ids=(),
                path_values={},
            )
        )


def test_collection_validates_offset_pagination_values():
    with pytest.raises(ValueError, match="limit"):
        siren().collection(
            SirenCollectionRequest(
                resource_name="record",
                items=(),
                collection_operation_ids=("list_records",),
                item_operation_ids=(),
                path_values={},
                pagination=OffsetPagination(limit=0, offset=0, count=0, has_next=False),
            )
        )


def test_ninja_adapter_returns_collection_response():
    response = NinjaExtraSirenResponseAdapter(siren()).collection(
        SirenCollectionRequest(
            resource_name="record",
            items=({"slug": "architecture"},),
            collection_operation_ids=("list_records",),
            item_operation_ids=(),
            path_values={},
        ),
        status_code=206,
        headers={"Accept-Ranges": "items"},
    )

    assert response.status_code == 206
    assert response.content_type == "application/vnd.siren+json"
    assert response.headers == {"Accept-Ranges": "items"}
    assert response.body["class"] == ["collection", "record"]
