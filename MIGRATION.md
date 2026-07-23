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
from modwire_siren import SirenContext
from modwire_siren.extras import siren

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

Version 2 derives a resource from canonical routes:

```text
/records
/records/{record_id}
```

The collection segment is plural. The entity parameter is the singular resource name followed by
`_id`. Operations require unique `operationId` values. Child entity actions may extend the entity
path without introducing another path parameter.

```yaml
paths:
  /records:
    get:
      operationId: list_records
  /records/{record_id}:
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
