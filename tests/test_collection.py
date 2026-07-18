from typing import Any

import pytest

from modwire_siren import (
    CustomPagination,
    ModwireSirenFactory,
    NinjaExtraSirenController,
    NinjaExtraSirenResponseAdapter,
    OffsetPagination,
    OpenApiError,
    PaginationLinkInput,
    SirenCollectionRequest,
    siren_collection,
)


class RecordOrm:
    def __init__(self, slug: str, title: str):
        self.slug = slug
        self.title = title


class RecordOrmSerializer:
    def serialize(self, value: Any) -> dict[str, str]:
        if not isinstance(value, RecordOrm):
            raise TypeError(f"Unsupported ORM value: {type(value).__name__}")
        return {"slug": value.slug, "title": value.title}


class Request:
    def __init__(self, origin: str):
        self.origin = origin

    def build_absolute_uri(self, path: str) -> str:
        return f"{self.origin.rstrip('/')}/{path.lstrip('/')}"


class QueryParams:
    def __init__(self, pairs: tuple[tuple[str, Any], ...]):
        self._pairs = pairs

    def lists(self) -> tuple[tuple[str, tuple[Any, ...]], ...]:
        grouped: dict[str, list[Any]] = {}
        for name, value in self._pairs:
            grouped.setdefault(name, []).append(value)
        return tuple((name, tuple(values)) for name, values in grouped.items())


class RequestWithQuery(Request):
    def __init__(self, origin: str, pairs: tuple[tuple[str, Any], ...]):
        super().__init__(origin)
        self.GET = QueryParams(pairs)


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
                "collection-operations": ("search_records", "import_records"),
            },
            "get": {"operationId": "get_record", "summary": "Get record"},
            "patch": {"operationId": "revise_record", "summary": "Revise record"},
        },
        "/records/search": {
            "post": {
                "operationId": "search_records",
                "summary": "Search records",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["query"],
                                "properties": {"query": {"type": "string"}},
                            }
                        }
                    }
                },
            },
        },
        "/records/import": {
            "post": {"operationId": "import_records", "summary": "Import records"},
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


def test_collection_only_resource_projects_items_without_item_self_links():
    schema = {
        "openapi": "3.1.0",
        "paths": {
            "/languages": {
                "x-siren-resource": {
                    "name": "language",
                    "class": "language",
                    "identifier": "id",
                    "path-parameters": {},
                    "relations": {},
                    "collection-only": True,
                },
                "get": {"operationId": "list_languages"},
            },
        },
    }

    document = ModwireSirenFactory.standard(schema, "https://api.test").collection(
        SirenCollectionRequest(
            resource_name="language",
            items=({"id": "python", "name": "Python"},),
            collection_operation_ids=("list_languages",),
            item_operation_ids=(),
            path_values={},
        )
    )

    assert document["class"] == ["collection", "language"]
    assert document["links"][0]["href"] == "https://api.test/languages"
    assert document["entities"][0] == {
        "rel": ["item"],
        "class": ["language"],
        "properties": {"id": "python", "name": "Python"},
        "links": [],
        "actions": [],
        "entities": [],
    }


def test_collection_only_must_be_explicit_to_omit_identifier_path_mapping():
    schema = {
        "openapi": "3.1.0",
        "paths": {
            "/languages": {
                "x-siren-resource": {
                    "name": "language",
                    "class": "language",
                    "identifier": "id",
                    "path-parameters": {},
                    "relations": {},
                },
                "get": {"operationId": "list_languages"},
            },
        },
    }

    with pytest.raises(OpenApiError, match=r"identifier 'id'.*path-parameters"):
        ModwireSirenFactory.standard(schema, "https://api.test")


def test_collection_projects_declared_subpath_actions_with_request_schema_fields():
    document = siren().collection(
        SirenCollectionRequest(
            resource_name="record",
            items=(),
            collection_operation_ids=("search_records", "list_records"),
            item_operation_ids=(),
            path_values={},
        )
    )

    assert document["links"][0]["href"] == "https://api.test/records"
    assert [action["name"] for action in document["actions"]] == ["search_records", "list_records"]
    assert document["actions"][0]["href"] == "https://api.test/records/search"
    assert [field["name"] for field in document["actions"][0]["fields"]] == ["query"]


def test_collection_keeps_collection_self_href_when_only_advertising_declared_subpath_action():
    document = siren().collection(
        SirenCollectionRequest(
            resource_name="record",
            items=(),
            collection_operation_ids=("search_records",),
            item_operation_ids=(),
            path_values={},
        )
    )

    assert document["links"][0]["href"] == "https://api.test/records"
    assert [action["href"] for action in document["actions"]] == ["https://api.test/records/search"]


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


def test_collection_pagination_preserves_repeated_base_query_values():
    schema = {
        "openapi": "3.1.0",
        "paths": {
            "/records": {
                "get": {"operationId": "list_records"},
            },
            "/records/{record_slug}": {
                "x-siren-resource": {
                    "name": "record",
                    "class": "record",
                    "identifier": "slug",
                    "path-parameters": {"record_slug": "slug"},
                    "relations": {},
                },
                "get": {"operationId": "get_record"},
            },
        },
    }

    document = ModwireSirenFactory.standard(schema, "https://api.test").collection(
        SirenCollectionRequest(
            resource_name="record",
            items=(),
            collection_operation_ids=("list_records",),
            item_operation_ids=(),
            path_values={},
            pagination=OffsetPagination(limit=2, offset=2, count=10, has_next=True),
            query=(
                ("limit", 2),
                ("offset", 2),
                ("tag", "alpha"),
                ("tag", "beta"),
                ("category", "docs"),
                ("category", "guide"),
            ),
        )
    )

    assert document["links"][1]["href"] == (
        "https://api.test/records?tag=alpha&tag=beta&category=docs&category=guide&limit=2&offset=0"
    )
    assert document["links"][3]["href"] == (
        "https://api.test/records?tag=alpha&tag=beta&category=docs&category=guide&limit=2&offset=4"
    )


def test_collection_custom_pagination_accepts_repeated_query_pairs():
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
                    PaginationLinkInput(rel="self", query=(("tag", "alpha"), ("tag", "beta"), ("cursor", "abc"))),
                    PaginationLinkInput(rel="next", query={"tag": ("gamma", "delta"), "cursor": "def"}),
                ),
            ),
        )
    )

    assert document["links"][0]["href"] == "https://api.test/records?tag=alpha&tag=beta&cursor=abc"
    assert document["links"][1]["href"] == "https://api.test/records?tag=gamma&tag=delta&cursor=def"


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


def test_collection_rejects_undeclared_subpath_collection_operations():
    with pytest.raises(OpenApiError, match="do not share path"):
        siren().collection(
            SirenCollectionRequest(
                resource_name="record",
                items=(),
                collection_operation_ids=("list_records", "revise_record"),
                item_operation_ids=(),
                path_values={},
            )
        )


def test_declared_collection_subpath_operation_must_be_owned_by_resource_collection():
    schema = {
        "openapi": "3.1.0",
        "paths": {
            "/records": {
                "get": {"operationId": "list_records"},
            },
            "/records/{record_slug}": {
                "x-siren-resource": {
                    "name": "record",
                    "class": "record",
                    "identifier": "slug",
                    "path-parameters": {"record_slug": "slug"},
                    "relations": {},
                    "collection-operations": ("search_users",),
                },
                "get": {"operationId": "get_record"},
            },
            "/users/search": {
                "post": {"operationId": "search_users"},
            },
        },
    }

    with pytest.raises(OpenApiError, match="Collection operation 'search_users' is not owned"):
        ModwireSirenFactory.standard(schema, "https://api.test")


def test_declared_collection_subpath_operation_cannot_require_unavailable_item_path_values():
    schema = {
        "openapi": "3.1.0",
        "paths": {
            "/records": {
                "get": {"operationId": "list_records"},
            },
            "/records/{record_slug}": {
                "x-siren-resource": {
                    "name": "record",
                    "class": "record",
                    "identifier": "slug",
                    "path-parameters": {"record_slug": "slug"},
                    "relations": {},
                    "collection-operations": ("archive_record",),
                },
                "get": {"operationId": "get_record"},
            },
            "/records/{record_slug}/archive": {
                "post": {"operationId": "archive_record"},
            },
        },
    }

    with pytest.raises(OpenApiError, match="unmapped path parameters"):
        ModwireSirenFactory.standard(schema, "https://api.test")


def test_collection_rejects_declared_subpath_actions_with_missing_path_values():
    schema = {
        "openapi": "3.1.0",
        "paths": {
            "/workspaces/{workspace_id}/records": {
                "get": {"operationId": "list_workspace_records"},
            },
            "/workspaces/{workspace_id}/records/{record_slug}": {
                "x-siren-resource": {
                    "name": "record",
                    "class": "record",
                    "identifier": "slug",
                    "path-parameters": {"workspace_id": "workspace_id", "record_slug": "slug"},
                    "relations": {},
                    "collection-operations": ("import_workspace_records",),
                },
                "get": {"operationId": "get_workspace_record"},
            },
            "/workspaces/{workspace_id}/records/import": {
                "post": {"operationId": "import_workspace_records"},
            },
        },
    }

    with pytest.raises(OpenApiError, match="workspace_id"):
        ModwireSirenFactory.standard(schema, "https://api.test").collection(
            SirenCollectionRequest(
                resource_name="record",
                items=(),
                collection_operation_ids=("list_workspace_records", "import_workspace_records"),
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


def test_ninja_adapter_preserves_collection_request_query():
    response = NinjaExtraSirenResponseAdapter(siren()).collection(
        SirenCollectionRequest(
            resource_name="record",
            items=(),
            collection_operation_ids=("list_records",),
            item_operation_ids=(),
            path_values={},
            pagination=OffsetPagination(limit=2, offset=2, count=10, has_next=True),
            query=(("tag", "alpha"), ("tag", "beta"), ("offset", 2)),
        )
    )

    assert response.body["links"][1]["href"] == "https://api.test/records?tag=alpha&tag=beta&limit=2&offset=0"


def test_ninja_adapter_serializes_collection_items_with_adapter_serializer():
    response = NinjaExtraSirenResponseAdapter(siren(), property_serializer=RecordOrmSerializer()).collection(
        SirenCollectionRequest(
            resource_name="record",
            items=(RecordOrm("architecture", "Architecture"),),
            collection_operation_ids=("list_records",),
            item_operation_ids=("get_record",),
            path_values={},
        )
    )

    assert response.body["entities"][0]["properties"] == {"slug": "architecture", "title": "Architecture"}
    assert response.body["entities"][0]["links"][0]["href"] == "https://api.test/records/architecture"


def test_ninja_adapter_for_request_uses_request_base_url_resolver_for_collections():
    siren_factory = ModwireSirenFactory.web(
        SCHEMA,
        base_url_resolver=lambda request: request.build_absolute_uri("/api/"),
    )
    response = NinjaExtraSirenResponseAdapter.for_request(
        siren_factory=siren_factory,
        request=Request("https://tenant.test"),
    ).collection(
        SirenCollectionRequest(
            resource_name="record",
            items=({"slug": "architecture"},),
            collection_operation_ids=("list_records",),
            item_operation_ids=("get_record",),
            path_values={},
        )
    )

    assert response.body["links"][0]["href"] == "https://tenant.test/api/records"
    assert response.body["entities"][0]["links"][0]["href"] == "https://tenant.test/api/records/architecture"


def test_siren_collection_response_serializes_items_with_decorator_serializer():
    class RecordController(NinjaExtraSirenController):
        @siren_collection(resource="record", operations=("list_records",), serializer=RecordOrmSerializer())
        def list_records(self) -> tuple[RecordOrm, ...]:
            return (RecordOrm("architecture", "Architecture"),)

    response = RecordController(siren()).list_records()

    assert response.body["entities"][0]["properties"] == {"slug": "architecture", "title": "Architecture"}


def test_siren_collection_response_uses_request_query_for_pagination_links():
    class RecordController(NinjaExtraSirenController):
        @siren_collection(
            resource="record",
            operations=("list_records",),
            pagination=OffsetPagination(limit=2, offset=2, count=10, has_next=True),
        )
        def list_records(self, request: Any) -> tuple[dict[str, str], ...]:
            return ()

    response = RecordController(siren()).list_records(
        RequestWithQuery("https://api.test", (("tag", "alpha"), ("tag", "beta"), ("offset", 2)))
    )

    assert response.body["links"][1]["href"] == "https://api.test/records?tag=alpha&tag=beta&limit=2&offset=0"


def test_siren_collection_response_reports_clear_item_serialization_failures():
    class RecordController(NinjaExtraSirenController):
        @siren_collection(resource="record", operations=("list_records",))
        def list_records(self) -> tuple[object, ...]:
            return (object(),)

    with pytest.raises(TypeError, match="Siren property serialization requires"):
        RecordController(siren()).list_records()


def test_siren_collection_response_handles_no_content_status_cleanly():
    class RecordController(NinjaExtraSirenController):
        @siren_collection(resource="record", operations=(), status_code=204)
        def delete_all_records(self) -> None:
            return None

    response = RecordController(siren()).delete_all_records()

    assert response.status_code == 204
    assert response.body is None
    assert response.content_type is None


def test_siren_collection_response_rejects_no_content_body():
    class RecordController(NinjaExtraSirenController):
        @siren_collection(resource="record", operations=(), status_code=204)
        def delete_all_records(self) -> tuple[dict, ...]:
            return ()

    with pytest.raises(ValueError, match="must not include a body"):
        RecordController(siren()).delete_all_records()
