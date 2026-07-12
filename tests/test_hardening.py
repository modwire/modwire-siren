import pytest

from modwire_siren import ModwireSirenFactory, OpenApiError, SirenEntityRequest
from modwire_siren.openapi.factory import OpenApiCatalogFactory
from modwire_siren.openapi.href import OpenApiHrefResolver
from modwire_siren.openapi.resolver import ComponentSchemaResolver
from modwire_siren.openapi.resource import OpenApiResourceReader
from modwire_siren.profile.document import ProfileDocument
from modwire_siren.profile.standard import ProfileStandard


def resource(name: str, path_parameter: str = "id") -> dict:
    return {
        "name": name,
        "class": name,
        "identifier": "id",
        "path-parameters": {path_parameter: "id"},
        "relations": {},
    }


CATALOGS = OpenApiCatalogFactory(
    OpenApiResourceReader(ProfileDocument(ProfileStandard.load()))
)


def test_catalog_rejects_duplicate_operation_and_resource_names():
    with pytest.raises(OpenApiError, match=r"Duplicate OpenAPI operationId.*same"):
        CATALOGS.create(
            {"paths": {"/a": {"get": {"operationId": "same"}}, "/b": {"get": {"operationId": "same"}}}}
        )

    with pytest.raises(OpenApiError, match=r"Duplicate Siren resource name.*record"):
        CATALOGS.create(
            {
                "paths": {
                    "/a/{id}": {"x-siren-resource": resource("record"), "get": {"operationId": "a"}},
                    "/b/{id}": {"x-siren-resource": resource("record"), "get": {"operationId": "b"}},
                }
            }
        )


def test_operation_reader_merges_path_parameters_with_operation_overrides():
    catalog = CATALOGS.create(
        {
            "paths": {
                "/records": {
                    "parameters": [
                        {"in": "query", "name": "locale", "required": False, "schema": {"type": "string"}}
                    ],
                    "get": {
                        "operationId": "list_records",
                        "parameters": [
                            {"in": "query", "name": "locale", "required": True, "schema": {"type": "string"}},
                            {"in": "query", "name": "page", "required": False, "schema": {"type": "integer"}},
                        ],
                    },
                }
            }
        }
    )

    fields = catalog.operation("list_records").fields
    assert [(field.name, field.required) for field in fields] == [("locale", True), ("page", False)]


def test_schema_resolver_recursively_resolves_nested_compositions_without_mutation():
    components = {
        "Tag": {"type": "string", "enum": ["stable"]},
        "Metadata": {"type": "object", "properties": {"tag": {"$ref": "#/components/schemas/Tag"}}},
    }
    schema = {
        "type": "array",
        "items": {
            "allOf": [
                {"$ref": "#/components/schemas/Metadata"},
                {"properties": {"alternative": {"anyOf": [{"$ref": "#/components/schemas/Tag"}]}}},
            ]
        },
    }

    resolved = ComponentSchemaResolver(components).resolve(schema)

    assert resolved["items"]["properties"]["tag"] == {"type": "string", "enum": ["stable"]}
    assert resolved["items"]["properties"]["alternative"]["anyOf"][0]["type"] == "string"
    assert "$ref" in schema["items"]["allOf"][0]


def test_schema_resolver_rejects_circular_references():
    resolver = ComponentSchemaResolver(
        {
            "A": {"type": "object", "properties": {"b": {"$ref": "#/components/schemas/B"}}},
            "B": {"type": "object", "properties": {"a": {"$ref": "#/components/schemas/A"}}},
        }
    )

    with pytest.raises(OpenApiError, match="Circular OpenAPI schema reference: A -> B -> A"):
        resolver.resolve({"$ref": "#/components/schemas/A"})


def test_href_resolver_encodes_values_and_reports_missing_placeholders():
    resolver = OpenApiHrefResolver("https://api.test/root")
    assert resolver.resolve("/records/{id}", {"id": "a/b ?"}) == "https://api.test/root/records/a%2Fb%20%3F"
    with pytest.raises(OpenApiError, match="Missing path value 'id'"):
        resolver.resolve("/records/{id}", {})


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
