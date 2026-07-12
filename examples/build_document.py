from modwire_siren import ModwireSirenFactory, SirenEntityRequest

openapi_schema = {
    "openapi": "3.1.0",
    "paths": {
        "/records/{record_slug}": {
            "x-siren-resource": {
                "name": "record",
                "class": "record",
                "identifier": "slug",
                "path-parameters": {"record_slug": "slug"},
                "relations": {},
            },
            "x-siren-ui-profile": {
                "profile": "https://raw.githubusercontent.com/modwire/modwire-siren/main/docs/siren-ui-profile/README.md",
                "presentation": {"role": "detail", "label": "Architecture record"},
                "properties": {
                    "title": {"label": "Title", "importance": "primary"},
                },
            },
            "get": {"operationId": "get_record", "summary": "Get record"},
        }
    },
}

siren = ModwireSirenFactory.standard(openapi_schema, "https://api.example.com/")
document = siren.document(
    SirenEntityRequest(
        resource_name="record",
        properties={"slug": "architecture/aggregate", "title": "Architecture"},
        operation_ids=("get_record",),
        path_values={},
        entities=(),
    )
)
