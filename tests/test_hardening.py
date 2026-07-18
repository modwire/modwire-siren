import pytest

from modwire_siren import ModwireSirenFactory, OpenApiError, SirenEntityRequest


def resource(name: str, path_parameter: str = "id") -> dict:
    return {
        "name": name,
        "class": name,
        "identifier": "id",
        "path-parameters": {path_parameter: "id"},
        "relations": {},
    }


def test_catalog_rejects_duplicate_operation_and_resource_names():
    with pytest.raises(OpenApiError, match=r"Duplicate OpenAPI operationId.*same"):
        ModwireSirenFactory.standard(
            {"paths": {"/a": {"get": {"operationId": "same"}}, "/b": {"get": {"operationId": "same"}}}},
            "https://api.test",
        )

    with pytest.raises(OpenApiError, match=r"Duplicate Siren resource name.*record"):
        ModwireSirenFactory.standard(
            {
                "paths": {
                    "/a/{id}": {"x-siren-resource": resource("record"), "get": {"operationId": "a"}},
                    "/b/{id}": {"x-siren-resource": resource("record"), "get": {"operationId": "b"}},
                }
            },
            "https://api.test",
        )


def test_operation_reader_merges_path_parameters_with_operation_overrides():
    document = ModwireSirenFactory.standard(
        {
            "paths": {
                "/records/{id}": {
                    "x-siren-resource": resource("record"),
                    "parameters": [
                        {"in": "query", "name": "locale", "required": False, "schema": {"type": "string"}},
                    ],
                    "patch": {
                        "operationId": "revise_record",
                        "parameters": [
                            {"in": "query", "name": "locale", "required": True, "schema": {"type": "string"}},
                            {"in": "query", "name": "page", "required": False, "schema": {"type": "integer"}},
                        ],
                    },
                }
            }
        },
        "https://api.test",
    ).document(
        SirenEntityRequest(
            resource_name="record",
            properties={"id": "rec-1"},
            operation_ids=("revise_record",),
            path_values={},
            entities=(),
        )
    )

    fields = document["actions"][0]["fields"]
    assert [(field["name"], field["required"]) for field in fields] == [("locale", True), ("page", False)]


def test_schema_resolver_recursively_resolves_nested_compositions_without_mutation():
    components = {
        "Tag": {"type": "string", "enum": ["stable"]},
        "Metadata": {"type": "object", "properties": {"tag": {"$ref": "#/components/schemas/Tag"}}},
    }
    schema = {
        "type": "object",
        "properties": {
            "metadata": {"$ref": "#/components/schemas/Metadata"},
            "alternative": {"anyOf": [{"$ref": "#/components/schemas/Tag"}]},
        },
    }
    openapi = {
        "components": {"schemas": components},
        "paths": {
            "/records/{id}": {
                "x-siren-resource": resource("record"),
                "patch": {
                    "operationId": "revise_record",
                    "requestBody": {"content": {"application/json": {"schema": schema}}},
                },
            }
        },
    }

    document = ModwireSirenFactory.standard(openapi, "https://api.test").document(
        SirenEntityRequest(
            resource_name="record",
            properties={"id": "rec-1"},
            operation_ids=("revise_record",),
            path_values={},
            entities=(),
        )
    )

    fields = {field["name"]: field for field in document["actions"][0]["fields"]}
    assert fields["metadata"]["schema"]["properties"]["tag"] == {"type": "string", "enum": ["stable"]}
    assert fields["alternative"]["schema"]["anyOf"][0]["type"] == "string"
    assert "$ref" in schema["properties"]["metadata"]


def test_schema_resolver_rejects_circular_references():
    schema = {
        "components": {
            "schemas": {
                "A": {"type": "object", "properties": {"b": {"$ref": "#/components/schemas/B"}}},
                "B": {"type": "object", "properties": {"a": {"$ref": "#/components/schemas/A"}}},
            }
        },
        "paths": {
            "/records/{id}": {
                "x-siren-resource": resource("record"),
                "patch": {
                    "operationId": "revise_record",
                    "requestBody": {
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/A"}}}
                    },
                },
            }
        },
    }

    with pytest.raises(OpenApiError, match="Circular OpenAPI schema reference: A -> B -> A"):
        ModwireSirenFactory.standard(schema, "https://api.test")


def test_href_resolver_encodes_values_and_reports_missing_placeholders():
    document = ModwireSirenFactory.standard(
        {
            "paths": {
                "/records/{id}": {"x-siren-resource": resource("record"), "get": {"operationId": "get_record"}},
            }
        },
        "https://api.test/root",
    ).document(
        SirenEntityRequest(
            resource_name="record",
            properties={"id": "a/b ?"},
            operation_ids=(),
            path_values={},
            entities=(),
        )
    )

    assert document["links"][0]["href"] == "https://api.test/root/records/a%2Fb%20%3F"
    with pytest.raises(OpenApiError, match="Missing properties"):
        ModwireSirenFactory.standard(
            {
                "paths": {
                    "/records/{id}": {"x-siren-resource": resource("record"), "get": {"operationId": "get_record"}},
                }
            },
            "https://api.test/root",
        ).document(
            SirenEntityRequest(
                resource_name="record",
                properties={},
                operation_ids=(),
                path_values={},
                entities=(),
            )
        )


def test_entity_rejects_action_from_another_resource():
    schema = {
        "paths": {
            "/records/{id}": {"x-siren-resource": resource("record"), "get": {"operationId": "get_record"}},
            "/users/{id}": {"x-siren-resource": resource("user"), "delete": {"operationId": "delete_user"}},
        }
    }

    with pytest.raises(OpenApiError, match=r"delete_user.*do not belong to resource 'record'"):
        ModwireSirenFactory.standard(schema, "https://api.test").document(
            SirenEntityRequest(
                resource_name="record",
                properties={"id": "one"},
                operation_ids=("delete_user",),
                path_values={},
                entities=(),
            )
        )
