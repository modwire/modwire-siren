# modwire-siren

`modwire-siren` compiles a complete OpenAPI 3.1 document into a reusable Siren engine. At request
time, the engine turns application data and permissions into a Siren response with concrete links
and authorized actions.

Requires Python 3.12 or later.

## Install

```bash
python -m pip install modwire-siren
```

For local development:

```bash
uv sync --all-groups --frozen
make verify
```

Version 2 is a breaking rewrite. See [MIGRATION.md](MIGRATION.md) when upgrading from version 1.

<!-- generated:public-api:start -->
## Usage

This section is generated from the docstrings of the supported root imports. Run `make docs` after changing a public API example or its guidance.

### `siren`

Compile a complete OpenAPI 3.1 document into a reusable Siren engine.

Call this once during application startup, then call `engine.project(context)` for each
negotiated Siren response. OpenAPI defines links, methods, and candidate fields; the context's
capabilities decide which candidate actions are present in that response.

#### Example

```python
from modwire_siren import SirenContext, siren

openapi = {
    "openapi": "3.1.1",
    "info": {"title": "Records API", "version": "1.0"},
    "paths": {
        "/records": {"get": {"operationId": "list_records", "responses": {"200": {"description": "OK"}}}},
        "/records/{record_id}": {
            "parameters": [{"name": "record_id", "in": "path", "required": True, "schema": {"type": "string"}}],
            "get": {"operationId": "get_record", "responses": {"200": {"description": "OK"}}},
            "patch": {
                "operationId": "rename_record",
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
                "responses": {"200": {"description": "OK"}},
            },
        },
    },
}

engine = siren(openapi)
document = engine.project(
    SirenContext(
        base_url="https://api.example.com",
        resource="record",
        value={"id": "42", "title": "Architecture"},
        capabilities=frozenset({"get_record", "rename_record"}),
    )
)

assert document["actions"][0] == {
    "name": "get_record",
    "href": "https://api.example.com/records/42",
    "method": "GET",
}
```

#### OpenAPI requirements

The final plural static segment of a route is a collection; adding one path parameter forms
its entity route. Prefixes and nested collections are supported. Every non-root HTTP operation
needs a unique `operationId`. Local `#/components/parameters`, `#/components/requestBodies`,
and `#/components/schemas` references are resolved; external and path-item references are not.

#### Framework integration is one startup call

Give the framework-generated document directly to `siren()` after routes are registered:

```python
engine = siren(app.openapi())  # FastAPI
engine = siren(api.get_openapi_schema())  # Django Ninja / Django Ninja Extra
```

Supply request-specific data and allowed operation IDs in `SirenContext`, then return
`engine.project(context)` as `application/vnd.siren+json`. Set `root_path` when the Siren
entry point is mounted away from `/`.

### `SirenContext`

Supply runtime state used to project a Siren document.

Use the default `"entity"` scope for one resource, `"collection"` for a list, and `"root"`
for an API entry point. A resource is required outside root scope and is the singular name
derived from the collection route: `"record"` for `/records`. If the same resource appears
in multiple nested routes, `path_values` selects the route with matching parent parameters.

| Field | Purpose |
| --- | --- |
| `base_url` | Public origin joined with OpenAPI paths. |
| `scope` | `"root"`, `"collection"`, or `"entity"`. |
| `resource` | Derived singular resource name; required outside root. |
| `value` | Entity or collection properties and entity path parameters. |
| `items` | Entity mappings for a collection. |
| `path_values` | Missing path parameters, such as a parent resource ID. |
| `query` | Ordered query pairs for self and action links. |
| `capabilities` | Permitted OpenAPI `operationId` values. |

## Public API

The supported root imports below are generated from `modwire_siren.__all__`.

| Symbol | Purpose | Primary API |
| --- | --- | --- |
| `SirenContext` | Supply runtime state used to project a Siren document. | — |
| `siren` | Compile a complete OpenAPI 3.1 document into a reusable Siren engine. | — |
<!-- generated:public-api:end -->
