# Migration to 2.0.0

Version 2.0.0 replaces the version 1 projection library with a small OpenAPI-to-Siren engine. This
is a breaking release; version 1 imports, decorators, resource extensions, profiles, client, and
framework integrations no longer exist.

## What changed

Version 1 required applications to declare `x-siren-resource` metadata, register resource specs,
create Siren controllers, and project every entity or collection manually.

Version 2 treats OpenAPI as the structural contract. It derives resources from canonical paths,
compiles one immutable `SirenApi`, and projects a `SirenContext` at runtime.

```python
from modwire_siren import SirenContext, siren

engine = siren(openapi)
document = engine.project(
    SirenContext(
        base_url="https://api.example.com",
        resource="record",
        value={"id": "42", "title": "Architecture"},
        capabilities=frozenset({"get_record", "rename_record"}),
    )
)
```

## Removed APIs

Remove all use of these version 1 APIs:

- `ModwireSiren` and `ModwireSirenFactory`
- `SirenEntityRequest`, `SirenCollectionRequest`, and resource specs
- `x-siren-resource` injection and validation
- `siren_entity`, `siren_collection`, and `siren_resource`
- Ninja Extra and Django integrations
- UI profile support
- `SirenClient`

## OpenAPI requirements

Version 2 derives resources from conventional OpenAPI route segments. A collection ends in a
plural static segment; its entity route adds one path parameter. Prefixes, nested collections,
and arbitrary parameter names are supported:

```text
/api/v1/records
/accounts/{account}/records
/accounts/{account}/records/{record}
```

The resource name is derived from the final collection segment. Operations require unique
`operationId` values. Exact routes and static subpaths belong to their matching collection or
entity; a nested resource owns the longest matching route. Unsupported or ambiguous routes fail
at startup rather than silently omitting an operation.

```yaml
paths:
  /records:
    get:
      operationId: list_records
  /records/{record}:
    get:
      operationId: get_record
    patch:
      operationId: rename_record
```

## Django and Ninja

The package no longer owns a Django or Ninja adapter. Keep your existing controller routes. At
application setup, pass Ninja's generated OpenAPI document to `siren()`. At response time, build a
`SirenContext` from the request, response value, and application-owned capabilities. Return the
engine output when the request negotiates `application/vnd.siren+json`.

```python
engine = siren(api.get_openapi_schema())

document = engine.project(
    SirenContext(
        base_url=request.build_absolute_uri("/"),
        resource="record",
        value=result,
        capabilities=capabilities_for(request, result),
    )
)
```

Authorization and state remain application responsibilities. OpenAPI defines candidate actions;
`capabilities` determines which actions are advertised in this response.

## Manual construction

OpenAPI is the ordinary path. For exceptional cases, use `SirenBuilderService` directly:

```python
from modwire_siren.builder import SirenBuilderService
from modwire_siren.engine import SirenEngine

api = (
    SirenBuilderService()
    .add_resource("record", "record", "/records", "/records/{record_id}")
    .add_operation("record", "entity", "get_record", "GET", "/records/{record_id}")
    .build()
)

engine = SirenEngine(api)
```
