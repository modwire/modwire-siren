import pytest

from modwire_siren import ModwireSirenFactory, OpenApiError, SirenEntityRequest

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
    document = ModwireSirenFactory.standard(SCHEMA, "https://api.test/").document(
        SirenEntityRequest(
            resource_name="record",
            properties={"slug": "architecture/aggregate", "section_slug": "architecture"},
            operation_ids=("revise_record",),
            path_values={},
            entities=(),
        )
    )

    action = document["actions"][0]
    assert action["href"] == "https://api.test/records/architecture%2Faggregate"
    assert [field["name"] for field in action["fields"]] == ["dry_run", "title", "tags"]
    assert action["fields"][0]["type"] == "checkbox"
    assert action["fields"][2]["type"] == "json"
    assert document["links"][1] == {
        "rel": ["section"],
        "href": "https://api.test/sections/architecture",
        "title": "section",
        "type": "application/vnd.siren+json",
    }


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


def test_openapi_rejects_singular_relation_iterables():
    siren = ModwireSirenFactory.standard(SCHEMA, "https://api.test/")

    with pytest.raises(OpenApiError, match="singular value"):
        siren.document(
            SirenEntityRequest(
                resource_name="record",
                properties={"slug": "architecture", "section_slug": ["architecture", "billing"]},
                operation_ids=(),
                path_values={},
                entities=(),
            )
        )


def test_openapi_rejects_operations_without_stable_ids():
    with pytest.raises(OpenApiError, match="operationId"):
        ModwireSirenFactory.standard({"paths": {"/records": {"get": {}}}}, "https://api.test")


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
        ModwireSirenFactory.standard(schema, "https://api.test")


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
        ModwireSirenFactory.standard(schema, "https://api.test")


def test_openapi_requires_resource_identifier_to_be_path_resolvable():
    schema = {
        "paths": {
            "/records/{record_slug}": {
                "x-siren-resource": {
                    "name": "record",
                    "class": "record",
                    "identifier": "id",
                    "path-parameters": {"record_slug": "slug"},
                    "relations": {},
                },
                "get": {"operationId": "get_record"},
            }
        }
    }

    with pytest.raises(OpenApiError, match=r"identifier 'id'.*path-parameters"):
        ModwireSirenFactory.standard(schema, "https://api.test")


def test_openapi_rejects_resource_owned_sub_actions_with_extra_path_parameters():
    schema = {
        "paths": {
            "/records/{record_id}": {
                "x-siren-resource": {
                    "name": "record",
                    "class": "record",
                    "identifier": "id",
                    "path-parameters": {"record_id": "id"},
                    "relations": {},
                    "operations": ("comment_record",),
                },
                "get": {"operationId": "get_record"},
            },
            "/records/{record_id}/comments/{comment_id}": {
                "post": {"operationId": "comment_record"},
            },
        }
    }

    with pytest.raises(OpenApiError, match="comment_id"):
        ModwireSirenFactory.standard(schema, "https://api.test")


def test_openapi_accepts_json_array_resource_operation_metadata():
    schema = {
        "paths": {
            "/records": {
                "get": {"operationId": "list_records"},
            },
            "/records/{record_id}": {
                "x-siren-resource": {
                    "name": "record",
                    "class": "record",
                    "identifier": "id",
                    "path-parameters": {"record_id": "id"},
                    "relations": {},
                    "operations": ["archive_record"],
                    "collection-operations": ["search_records"],
                },
                "get": {"operationId": "get_record"},
            },
            "/records/{record_id}/archive": {
                "post": {"operationId": "archive_record"},
            },
            "/records/search": {
                "post": {"operationId": "search_records"},
            },
        }
    }

    document = ModwireSirenFactory.standard(schema, "https://api.test").document(
        SirenEntityRequest(
            resource_name="record",
            properties={"id": "architecture"},
            operation_ids=("archive_record",),
            path_values={},
            entities=(),
        )
    )

    assert document["actions"][0]["href"] == "https://api.test/records/architecture/archive"
