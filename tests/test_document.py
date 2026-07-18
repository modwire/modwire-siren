from modwire_siren import ModwireSirenFactory, SirenEntityRequest


def test_public_projection_is_the_wire_format_source_of_truth():
    schema = {
        "paths": {
            "/records/{record_slug}": {
                "x-siren-resource": {
                    "name": "record",
                    "class": "record",
                    "identifier": "slug",
                    "path-parameters": {"record_slug": "slug"},
                    "relations": {},
                },
                "delete": {
                    "operationId": "close",
                    "summary": "Close record",
                    "parameters": [
                        {"in": "query", "name": "force", "required": False, "schema": {"type": "boolean"}},
                    ],
                },
            }
        }
    }

    document = ModwireSirenFactory.standard(schema, "https://api.test").document(
        SirenEntityRequest(
            resource_name="record",
            properties={"slug": "architecture/aggregate"},
            operation_ids=("close",),
            path_values={},
            entities=(),
        )
    )

    assert document == {
        "class": ["record"],
        "properties": {"slug": "architecture/aggregate"},
        "entities": [],
        "actions": [
            {
                "name": "close",
                "href": "https://api.test/records/architecture%2Faggregate",
                "method": "DELETE",
                "title": "Close record",
                "type": "application/json",
                "fields": [
                    {
                        "name": "force",
                        "type": "checkbox",
                        "required": False,
                        "title": "force",
                        "options": [],
                        "schema": {},
                    }
                ],
            }
        ],
        "links": [
            {
                "rel": ["self"],
                "href": "https://api.test/records/architecture%2Faggregate",
                "title": "record",
                "type": "application/vnd.siren+json",
            }
        ],
    }
