import pytest

from modwire_siren import ModwireSirenFactory, OpenApiError, SirenEntityRequest
from modwire_siren.factories.action import SirenActionFactory
from modwire_siren.factories.field import OpenApiSirenFieldFactory
from modwire_siren.openapi.factory import OpenApiCatalogFactory
from modwire_siren.openapi.href import OpenApiHrefResolver
from modwire_siren.policies.field_type import OpenApiSirenFieldTypeResolver

SCHEMA = {
    "openapi": "3.1.0",
    "paths": {
        "/sections/{section_slug}": {
            "x-siren-resource": {
                "name": "section",
                "class": "section",
                "identifier": "slug",
                "path-parameters": {"section_slug": "slug"},
                "relations": {},
            },
            "get": {"operationId": "get_section", "summary": "Get section"},
        },
        "/records/{record_slug}": {
            "x-siren-resource": {
                "name": "record",
                "class": "record",
                "identifier": "slug",
                "path-parameters": {"record_slug": "slug"},
                "relations": {"section_slug": {"rel": "section", "resource": "section", "many": False}},
            },
            "patch": {
                "operationId": "revise_record",
                "summary": "Revise record",
                "parameters": [{"in": "query", "name": "dry_run", "required": False, "schema": {"type": "boolean"}}],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["title"],
                                "properties": {
                                    "title": {"type": "string"},
                                    "tags": {"type": "array", "items": {"type": "string"}},
                                },
                            }
                        }
                    }
                },
            },
        },
    },
}


def test_openapi_builds_actions_and_explicit_resource_metadata():
    catalog = OpenApiCatalogFactory.create(SCHEMA)
    hrefs = OpenApiHrefResolver("https://api.test/")
    fields = OpenApiSirenFieldFactory(OpenApiSirenFieldTypeResolver())

    action = SirenActionFactory(catalog, hrefs, fields).create(
        "revise_record", {"record_slug": "architecture/aggregate"}
    )
    resource = catalog.resource("record")

    assert action.href == "https://api.test/records/architecture%2Faggregate"
    assert [field.name for field in action.fields] == ["dry_run", "title", "tags"]
    assert action.fields[0].type == "checkbox"
    assert action.fields[2].type == "json"
    assert resource.identifier == "slug"
    assert resource.relations[0].field == "section_slug"


def test_composition_builds_links_and_only_runtime_legal_actions():
    siren = ModwireSirenFactory.standard(SCHEMA, "https://api.test/")

    document = siren.document(
        SirenEntityRequest(
            resource_name="record",
            properties={"slug": "architecture/aggregate", "section_slug": "architecture"},
            operation_ids=("revise_record",),
            path_values={},
            entities=(),
        )
    )

    assert document["class"] == ["record"]
    assert document["links"][0]["rel"] == ["self"]
    assert document["links"][0]["href"].endswith("/records/architecture%2Faggregate")
    assert document["links"][1]["rel"] == ["section"]
    assert document["links"][1]["href"].endswith("/sections/architecture")
    assert [action["name"] for action in document["actions"]] == ["revise_record"]


def test_openapi_rejects_operations_without_stable_ids():
    with pytest.raises(OpenApiError, match="operationId"):
        OpenApiCatalogFactory.create({"paths": {"/records": {"get": {}}}})


def test_openapi_requires_explicit_resource_path_parameter_mapping():
    schema = {
        "paths": {
            "/records/{record_slug}": {
                "x-siren-resource": {
                    "name": "record",
                    "class": "record",
                    "identifier": "slug",
                    "relations": {},
                },
                "get": {"operationId": "get_record"},
            }
        }
    }

    with pytest.raises(ValueError, match="path-parameters"):
        OpenApiCatalogFactory.create(schema)


def test_openapi_rejects_unknown_schema_references():
    schema = {
        "paths": {
            "/records": {
                "post": {
                    "operationId": "create_record",
                    "requestBody": {
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Missing"}}}
                    },
                }
            }
        }
    }

    with pytest.raises(OpenApiError, match="Unknown OpenAPI schema reference"):
        OpenApiCatalogFactory.create(schema)
