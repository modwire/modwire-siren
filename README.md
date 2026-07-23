# modwire-siren

`modwire-siren` compiles a conventional OpenAPI document into a validated Siren API graph and
projects runtime contexts into Siren documents.

Version 2.0.0 is a complete breaking rewrite. Read [MIGRATION.md](MIGRATION.md) before upgrading
from version 1.

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

The generated document contains concrete links and only the actions named in `capabilities`.

## OpenAPI contract

Routes use a framework-neutral, segment-based grammar. A resource collection ends in a plural
static segment; its entity route adds one path parameter. Prefixes and nested collections are
allowed, and parameter names are not prescribed:

```text
/api/v1/records
/accounts/{account}/records
/accounts/{account}/records/{record}
```

The singular resource name is derived from that final collection segment. A collection route may
stand alone. Operations on its exact path or static subpaths belong to its collection; operations
on an entity path or static subpaths belong to its entity. Nested resources take ownership over a
parent subpath, so `/accounts/{account}/records` belongs to `record`, not to `account`. Parameter
segments must be unchanged from the owning route: adding, removing, renaming, or reordering one
is unsupported. The longest matching route owns an operation; any tie is rejected.

`/` is the Siren entry point, not a resource route, so OpenAPI operations declared there are
unsupported. Every OpenAPI operation must have exactly one owner and an `operationId`; unsupported
or ambiguous routes and duplicate derived resource names fail compilation explicitly.

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
compatible sources. `siren(openapi)` accepts a complete, valid OpenAPI 3.1 document and validates
it before projection. `SirenEngine` projects root, collection, and entity contexts.

The compiler follows local `#/components/parameters`, `#/components/requestBodies`, and
`#/components/schemas` references used by projected actions. External references are intentionally
outside the supplier contract.

Action fields use only `path` and `query` parameters. Parameter identity is `(name, in)`;
operation-level declarations replace matching path-level declarations, while `path` parameters
remain routing values rather than action fields. Header and cookie parameters are unsupported.
Request bodies must offer `application/json` when they declare media content; it is selected even
when other media types appear. This keeps the observable Siren field contract deterministic.

`SirenContext.query` supplies ordered query pairs for projected self and action links. Repeated
keys are preserved, keys and scalar values are percent-encoded, and empty or `None` values render
as `key=`. Query values must be scalar; mappings and sequences are rejected. Root resource links
do not inherit the root self-link query state.

## Advanced use

The root package exports the normal application API:

```python
from modwire_siren import SirenContext, siren
```

The application compiles its OpenAPI document once at startup. For a mounted Siren entry point,
pass its path explicitly:

```python
engine = siren(openapi, root_path="/siren/")
```

Framework adapters are intentionally outside the package. A Django or Ninja application obtains
its generated OpenAPI document, creates an engine with `siren(openapi)`, builds a `SirenContext`
from the request and result, then returns `engine.project(context)` when Siren is negotiated.

<!-- generated:public-api:start -->
## Public API

The supported root imports below are generated from `modwire_siren.__all__`.

| Symbol | Purpose | Primary API |
| --- | --- | --- |
| `SirenContext` | Supply runtime state used to project a Siren document. | — |
| `siren` | Compile an OpenAPI document into a reusable Siren engine. | — |
<!-- generated:public-api:end -->
