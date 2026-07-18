from copy import deepcopy

from modwire_siren import SirenResourceSpec, inject_siren_resources
from modwire_siren.openapi import (
    add_siren_components,
    enrich_siren_openapi,
    rewrite_problem_responses,
    rewrite_siren_responses,
)

SCHEMA = {
    "openapi": "3.1.0",
    "paths": {
        "/records": {
            "get": {
                "operationId": "list_records",
                "summary": "List records",
                "tags": ["records"],
                "parameters": [
                    {"in": "query", "name": "limit", "schema": {"type": "integer"}},
                ],
                "responses": {
                    "200": {
                        "description": "Domain record list",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Record"},
                                },
                            },
                        },
                    },
                    "400": {
                        "description": "Bad request",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/DomainError"},
                            },
                        },
                    },
                },
            },
            "post": {
                "operationId": "create_record",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["title"],
                                "properties": {"title": {"type": "string"}},
                            },
                        },
                    },
                },
                "responses": {
                    "201": {"description": "Created"},
                    "409": {"description": "Conflict"},
                },
            },
            "delete": {
                "operationId": "delete_records",
                "responses": {
                    "204": {
                        "description": "Deleted",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                            },
                        },
                    },
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
            "get": {
                "operationId": "get_record",
                "responses": {
                    "200": {"description": "Record"},
                    "404": {"description": "Missing"},
                    "default": {"description": "Unexpected"},
                },
            },
        },
    },
    "components": {
        "schemas": {
            "Record": {
                "type": "object",
                "properties": {"slug": {"type": "string"}},
            },
            "DomainError": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
            },
            "SirenEntity": {
                "type": "object",
                "description": "Stale application-owned copy",
            },
        },
    },
}


def test_add_siren_components_preserves_existing_components_without_mutating_input():
    original = deepcopy(SCHEMA)

    schema = add_siren_components(SCHEMA)

    assert original == SCHEMA
    assert schema["components"]["schemas"]["Record"] == SCHEMA["components"]["schemas"]["Record"]
    assert "description" not in schema["components"]["schemas"]["SirenEntity"]
    assert {
        "SirenEntity",
        "SirenEmbeddedEntity",
        "SirenAction",
        "SirenField",
        "SirenLink",
        "Problem",
    } <= set(schema["components"]["schemas"])
    assert schema["components"]["schemas"]["SirenEntity"]["properties"]["actions"]["items"] == {
        "$ref": "#/components/schemas/SirenAction"
    }
    assert schema["components"]["schemas"]["Problem"]["required"] == ["title", "status"]


def test_enrich_siren_openapi_rewrites_response_media_types_and_preserves_operation_metadata():
    schema = enrich_siren_openapi(SCHEMA)

    list_records = schema["paths"]["/records"]["get"]
    assert list_records["operationId"] == "list_records"
    assert list_records["summary"] == "List records"
    assert list_records["tags"] == ["records"]
    assert list_records["parameters"] == SCHEMA["paths"]["/records"]["get"]["parameters"]
    assert list_records["responses"]["200"] == {
        "description": "Domain record list",
        "content": {
            "application/vnd.siren+json": {
                "schema": {"$ref": "#/components/schemas/SirenEntity"},
            },
        },
    }
    assert list_records["responses"]["400"] == {
        "description": "Bad request",
        "content": {
            "application/problem+json": {
                "schema": {"$ref": "#/components/schemas/Problem"},
            },
        },
    }

    create_record = schema["paths"]["/records"]["post"]
    assert create_record["requestBody"] == SCHEMA["paths"]["/records"]["post"]["requestBody"]
    assert create_record["responses"]["201"]["content"] == {
        "application/vnd.siren+json": {
            "schema": {"$ref": "#/components/schemas/SirenEntity"},
        },
    }
    assert create_record["responses"]["409"]["content"] == {
        "application/problem+json": {
            "schema": {"$ref": "#/components/schemas/Problem"},
        },
    }

    delete_records = schema["paths"]["/records"]["delete"]
    assert delete_records["responses"]["204"] == {"description": "Deleted"}

    get_record = schema["paths"]["/records/{record_slug}"]["get"]
    assert get_record["responses"]["404"]["content"] == {
        "application/problem+json": {
            "schema": {"$ref": "#/components/schemas/Problem"},
        },
    }
    assert get_record["responses"]["default"]["content"] == {
        "application/problem+json": {
            "schema": {"$ref": "#/components/schemas/Problem"},
        },
    }


def test_response_rewriters_support_custom_media_types():
    schema = rewrite_problem_responses(
        rewrite_siren_responses(SCHEMA, success_media_type="application/custom-siren+json"),
        problem_media_type="application/custom-problem+json",
    )

    assert schema["paths"]["/records"]["get"]["responses"]["200"]["content"] == {
        "application/custom-siren+json": {
            "schema": {"$ref": "#/components/schemas/SirenEntity"},
        },
    }
    assert schema["paths"]["/records"]["get"]["responses"]["400"]["content"] == {
        "application/custom-problem+json": {
            "schema": {"$ref": "#/components/schemas/Problem"},
        },
    }


def test_enrich_siren_openapi_composes_with_inject_siren_resources():
    schema = inject_siren_resources(
        SCHEMA,
        (
            SirenResourceSpec(
                name="record",
                path="/records/{record_slug}",
                resource_class="record",
                identifier="slug",
                path_parameters={"record_slug": "slug"},
                relations={},
            ),
        ),
    )

    schema = enrich_siren_openapi(schema)

    assert schema["paths"]["/records/{record_slug}"]["x-siren-resource"]["name"] == "record"
    assert schema["paths"]["/records/{record_slug}"]["get"]["responses"]["200"]["content"] == {
        "application/vnd.siren+json": {
            "schema": {"$ref": "#/components/schemas/SirenEntity"},
        },
    }


def test_enrich_siren_openapi_preserves_referenced_response_objects():
    schema = {
        "openapi": "3.1.0",
        "paths": {
            "/records": {
                "get": {
                    "operationId": "list_records",
                    "responses": {
                        "200": {"$ref": "#/components/responses/RecordCollection"},
                        "404": {"$ref": "#/components/responses/MissingRecord"},
                    },
                },
            },
        },
        "components": {
            "responses": {
                "RecordCollection": {"description": "Records"},
                "MissingRecord": {"description": "Missing"},
            },
        },
    }

    enriched = enrich_siren_openapi(schema)

    assert enriched["paths"]["/records"]["get"]["responses"] == schema["paths"]["/records"]["get"]["responses"]
