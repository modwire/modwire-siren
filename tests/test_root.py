import pytest

from modwire_siren import ModwireSirenFactory, OpenApiError

SCHEMA = {
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
        "/records/search": {
            "x-siren-resource": {
                "name": "record_search",
                "class": "record-search",
                "identifier": "",
                "path-parameters": {},
                "relations": {},
                "operations": ("search_records",),
                "singleton": True,
            },
            "post": {"operationId": "search_records"},
        },
        "/records/validate": {
            "x-siren-resource": {
                "name": "record_validation",
                "class": "record-validation",
                "identifier": "",
                "path-parameters": {},
                "relations": {},
                "operations": ("validate_records",),
                "singleton": True,
                "root-visible": True,
            },
            "post": {"operationId": "validate_records"},
        },
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
        "/workspaces/{workspace_id}/records": {
            "get": {"operationId": "list_workspace_records"},
        },
        "/workspaces/{workspace_id}/records/{record_slug}": {
            "x-siren-resource": {
                "name": "workspace_record",
                "class": "record",
                "identifier": "slug",
                "path-parameters": {"workspace_id": "workspace_id", "record_slug": "slug"},
                "relations": {},
            },
            "get": {"operationId": "get_workspace_record"},
        },
    },
}


def test_root_builds_api_entry_point_from_openapi_resources():
    document = ModwireSirenFactory.standard(SCHEMA, "https://api.test/api/").root(
        title="Example API",
        version="1.2.3",
        self_href="https://api.test/api/",
        service_desc_href="https://api.test/api/openapi.json",
        extra_links=(
            {
                "rel": ["browser"],
                "href": "https://api.test/browser/",
            },
        ),
    )

    assert document == {
        "class": ["api", "entry-point"],
        "properties": {"title": "Example API", "version": "1.2.3"},
        "links": [
            {"rel": ["self"], "href": "https://api.test/api/"},
            {
                "rel": ["records"],
                "href": "https://api.test/api/records",
                "type": "application/vnd.siren+json",
            },
            {
                "rel": ["validate"],
                "href": "https://api.test/api/records/validate",
                "type": "application/vnd.siren+json",
            },
            {
                "rel": ["languages"],
                "href": "https://api.test/api/languages",
                "type": "application/vnd.siren+json",
            },
            {
                "rel": ["service-desc"],
                "href": "https://api.test/api/openapi.json",
                "type": "application/vnd.oai.openapi+json;version=3.1",
            },
            {"rel": ["browser"], "href": "https://api.test/browser/"},
        ],
        "actions": [],
        "entities": [],
    }


def test_root_omits_optional_metadata_and_service_description():
    document = ModwireSirenFactory.standard(SCHEMA, "https://api.test").root(
        self_href="https://api.test/",
    )

    assert document["properties"] == {}
    assert [link["rel"] for link in document["links"]] == [["self"], ["records"], ["validate"], ["languages"]]


def test_root_rejects_invalid_extra_links():
    with pytest.raises(OpenApiError, match="rel and href"):
        ModwireSirenFactory.standard(SCHEMA, "https://api.test").root(
            self_href="https://api.test/",
            extra_links=({"rel": ["browser"]},),
        )
