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
        "/records": {
            "get": {
                "operationId": "list_records",
                "responses": {"200": {"description": "OK"}},
            }
        },
        "/records/{record_id}": {
            "parameters": [
                {
                    "name": "record_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "get": {
                "operationId": "get_record",
                "responses": {"200": {"description": "OK"}},
            },
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

assert document["actions"] == [
    {"name": "get_record", "href": "https://api.example.com/records/42", "method": "GET"},
    {
        "name": "rename_record",
        "href": "https://api.example.com/records/42",
        "method": "PATCH",
        "type": "application/json",
        "fields": [{"name": "title", "type": "string", "required": True}],
    },
]
```

#### OpenAPI requirements

The final plural static segment of a route is a collection; adding one path parameter forms
its entity route. Prefixes and nested collections are supported, including:

```text
/api/v1/records
/accounts/{account}/records
/accounts/{account}/records/{record}
```

Every non-root HTTP operation needs a unique `operationId`. Operations on collection or
entity paths, including their static subpaths, belong to that resource. The longest matching
route wins, so a nested resource owns `/accounts/{account}/records` rather than `account`.
The root document links only static collections with an input-free `GET` operation. Static
collection operations needing input or using another method, and standalone commands without
path parameters, are root actions when their operation IDs appear in the root context's
capabilities. Contextual operations remain on their owning collection or entity. Parameters
must be unchanged from the owning route: adding, removing, renaming, or reordering them is
unsupported. Ambiguous routes, unowned routes ending in a parameter, duplicate resource names,
missing operation IDs, and invalid OpenAPI fail compilation explicitly.

Local `#/components/parameters`, `#/components/requestBodies`, and `#/components/schemas`
references are resolved for actions. External and path-item references
are unsupported. Action fields come from query parameters and JSON request-body properties;
path parameters remain routing values. Header and cookie parameters are unsupported. If a
request body declares content, it must include `application/json`; that media type is projected
as the Siren action's `type`.

#### Framework integration is one startup call

Do not recreate your framework's routes, actions, or OpenAPI document in Siren-specific code.
Give the framework-generated document directly to `siren()` once, after routes are registered:

```python
# FastAPI
engine = siren(app.openapi())

# Django Ninja / Django Ninja Extra
engine = siren(api.get_openapi_schema())
```

That is the integration point: `siren()` derives the graph from the same contract your
framework already exposes. At response time, only supply the request-specific data and allowed
operation IDs in `SirenContext`, then return `engine.project(context)` as
`application/vnd.siren+json`. No builder, resource registration, route duplication, or
framework adapter is required.

#### Mounted entry point

Set `root_path` when the Siren entry point is mounted away from `/`:

```python
engine = siren(app.openapi(), root_path="/siren/")
```

Framework adapters are intentionally outside this package because the integration is already
the small startup call shown above.

### `SirenContext`

Supply runtime state used to project a Siren document.

Use the default `"entity"` scope for one resource, `"collection"` for a list, and `"root"`
for an API entry point. A resource is required outside root scope and is the singular name
derived from the collection route: `"record"` for `/records`. If the same resource appears
in multiple nested routes, `path_values` selects the route with matching parent parameters.

#### Collection example

```python
context = SirenContext(
    base_url="https://api.example.com",
    scope="collection",
    resource="record",
    items=(
        {"id": "42", "title": "Architecture"},
        {"id": "43", "title": "Systems"},
    ),
    query=(("page", 2),),
    capabilities=frozenset({"list_records"}),
)
document = engine.project(context)

assert document["links"] == [
    {"rel": ["self"], "href": "https://api.example.com/records?page=2"}
]
```

| Field | Purpose |
| --- | --- |
| `base_url` | Public origin joined with OpenAPI paths, for example `https://api.example.com`. |
| `scope` | `"root"`, `"collection"`, or `"entity"`. Root contexts have no resource. |
| `resource` | Derived singular resource name. Required outside the root. |
| `value` | Entity properties or collection-level properties. Also supplies entity path parameters. |
| `items` | Tuple of entity mappings for a collection. |
| `path_values` | Path parameters missing from `value`, such as a parent resource ID. |
| `query` | Ordered `(name, value)` pairs added to self and action links. |
| `capabilities` | Permitted OpenAPI `operationId` values to advertise as Siren actions. |

#### Nested routes and queries

For `/accounts/{account}/records/{record}`, supply the parent parameter separately:

```python
context = SirenContext(
    base_url="https://api.example.com",
    resource="record",
    path_values={"account": "acme"},
    value={"record": "42", "title": "Architecture"},
)
```

Path values are percent-encoded. Query pairs retain their order and repeated keys. Query
values must be scalar; booleans become lowercase `true` or `false`, and `None` becomes
an empty value. The root self link receives its query pairs, while root resource links do not.

## Public API

The supported root imports below are generated from `modwire_siren.__all__`.

| Symbol | Purpose | Primary API |
| --- | --- | --- |
| `SirenContext` | Supply runtime state used to project a Siren document. | — |
| `siren` | Compile a complete OpenAPI 3.1 document into a reusable Siren engine. | — |
<!-- generated:public-api:end -->
