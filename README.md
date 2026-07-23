# modwire-siren

`modwire-siren` compiles a conventional OpenAPI document into a validated Siren API graph and
projects runtime contexts into Siren documents.

Version 2.0.0 is a complete breaking rewrite. Read [MIGRATION.md](MIGRATION.md) before upgrading
from version 1.

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

The generated document contains concrete links and only the actions named in `capabilities`.

## OpenAPI contract

Resources use canonical collection and entity paths:

```text
/records
/records/{record_id}
```

The singular resource name is derived from the collection path. Entity parameters use the same
name followed by `_id`. Every supported operation requires an `operationId`.

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

`OpenApiSource` reads this structure into `SirenApi`. `SirenApiService` combines one or more
compatible sources. `SirenEngine` projects root, collection, and entity contexts.

## Advanced use

The root package exports the normal application API:

```python
from modwire_siren import SirenApiService, SirenContext
```

Advanced construction is available by direct import:

```python
from modwire_siren.builder import SirenBuilderService
from modwire_siren.engine import SirenEngine
from modwire_siren.sources import OpenApiSource, SirenSource
```

Framework adapters are intentionally outside the package. A Django or Ninja application obtains
its generated OpenAPI document, creates an engine with `siren(openapi)`, builds a `SirenContext`
from the request and result, then returns `engine.project(context)` when Siren is negotiated.

<!-- generated:public-api:start -->
## Public API

The supported root imports below are generated from `modwire_siren.__all__`.

| Symbol | Purpose | Primary API |
| --- | --- | --- |
| `SirenApiService` | Build a validated Siren API graph from one or more sources. | `build(schema: dict[str, typing.Any]) -> <class 'modwire_siren.contracts.SirenApi'>` |
| `SirenContext` | Supply runtime state used to project a Siren document. | — |
<!-- generated:public-api:end -->
