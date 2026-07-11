# modwire-siren

Typed Siren documents projected from OpenAPI without application-owned route maps.

Every external boundary is behind a package interface: catalog, href resolution, field policy,
field creation, link creation, resource hrefs, and serialization. `ModwireSirenFactory` is the
standard composition root; `ModwireSiren` is the small public façade.

## What Siren is

[Siren](https://github.com/kevinswiber/siren) is a hypermedia specification for representing an
entity together with the controls a client can use next. A JSON Siren document uses the media type
`application/vnd.siren+json` and can contain:

- `properties`: the entity's data;
- `entities`: related entities embedded in the representation;
- `links`: navigational controls identified by link relations; and
- `actions`: named state transitions, including the target, HTTP method, media type, and input
  fields.

This makes a Siren response more than a JSON snapshot. A client can discover available transitions
from the response instead of reconstructing URLs or duplicating server-side routing rules. Siren is
a community specification, not an IETF RFC. Its normative project specification is the
[Siren specification](https://github.com/kevinswiber/siren/blob/master/README.md); link relation
semantics come from [RFC 8288](https://www.rfc-editor.org/rfc/rfc8288), with standard relation names
listed in the [IANA Link Relations registry](https://www.iana.org/assignments/link-relations/).

## What this package adds

OpenAPI describes the API surface; Siren describes the controls available in a particular response.
`modwire-siren` joins the two: it reads routes, operations, request schemas, and the explicit
`x-siren-resource` metadata from one OpenAPI document, then projects runtime resource values into a
typed Siren entity. Applications therefore do not need to maintain a second route map for Siren
links and actions.

The package intentionally does not decide authorization. Callers pass the operation IDs that are
legal for the current entity and principal, and only those operations become actions. It also does
not serve HTTP responses itself; the framework layer remains responsible for content negotiation
and returning `Content-Type: application/vnd.siren+json`.

## Useful next improvements

The most valuable additions for this project would be:

1. Add framework response adapters that set the Siren content type and handle content negotiation,
   while keeping the core framework-independent.
2. Publish a machine-readable schema for `x-siren-resource` and validate it in editor/CI workflows,
   so mistakes are caught before application startup.
3. Add specification conformance fixtures for embedded entities, every action field type, and link
   relations, alongside the current unit tests.
4. Generate a complete example response in this README, not only the construction code, so users
   can immediately see the resulting wire format.
5. Document an authorization recipe showing how a policy selects the runtime `operation_ids`
   without leaking unavailable actions to clients.

<!-- generated:public-api:start -->
## Public API

The supported root imports below are generated from `modwire_siren.__all__`.

| Symbol | Purpose | Primary API |
| --- | --- | --- |
| `ModwireSiren` | Project validated entity requests into serialized Siren documents. | `document(request: modwire_siren.contracts.entity.SirenEntityRequest) -> dict[str, typing.Any]` |
| `ModwireSirenFactory` | Build the standard OpenAPI-backed Siren façade. | `standard(schema: dict[str, typing.Any], base_url: str) -> modwire_siren.facade.ModwireSiren` |
| `NinjaExtraSirenController` | Framework-light base for Ninja Extra controllers that emit Siren documents. | `siren_document(resource_name: str, properties: collections.abc.Mapping[str, typing.Any], operation_ids: tuple[str, ...], path_values: collections.abc.Mapping[str, typing.Any], entities: tuple[modwire_siren.contracts.entity.SirenEmbeddedEntity, ...] = ()) -> dict[str, typing.Any]` |
| `OpenApiError` | Report invalid or incomplete OpenAPI data used for Siren projection. | — |
| `SirenEntityDecorator` | Turn a controller method's property mapping into a Siren entity document. | — |
| `SirenEntityRequest` | Describe the resource data and allowed operations projected into one entity. | — |
| `__version__` | Installed distribution version. | — |

## Executable example

Source: [`build_document.py`](examples/build_document.py). This file is executed by the test suite.

```python
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
```
<!-- generated:public-api:end -->

## OpenAPI contract

```yaml
paths:
  /records/{record_slug}:
    x-siren-resource:
      name: record
      class: record
      identifier: slug
      path-parameters:
        record_slug: slug
      relations:
        section_slug:
          rel: section
          resource: section
          many: false
    patch:
      operationId: revise_record
      summary: Revise record
```

The strict `OpenApiResourceExtension` validates the extension. Unknown resources, incomplete path
mappings, absent operation IDs, and unknown schema references fail while building the catalog.

The Pydantic Siren contracts own wire aliases such as `class`, `type`, and `schema`.
`PydanticSirenSerializer` implements the `SirenSerializer` interface with one model dump; it does
not redeclare the wire schema.

## Django Ninja Extra

The controller adapter does not import Django or Ninja Extra, so the core package keeps no framework
dependency. It composes directly with Ninja Extra's controller and route decorators:

```python
from ninja_extra import ControllerBase, api_controller, route
from modwire_siren import ModwireSiren, NinjaExtraSirenController, SirenEntityDecorator

@api_controller("/records")
class RecordController(ControllerBase, NinjaExtraSirenController):
    def __init__(self, records: RecordService, siren: ModwireSiren):
        NinjaExtraSirenController.__init__(self, siren)
        self.records = records

    @route.get("/{record_slug}", operation_id="get_record")
    @SirenEntityDecorator("record", operations=("revise_record",))
    def get_record(self, record_slug: str):
        return self.records.get(record_slug)
```

The method returns only resource properties. `@SirenEntityDecorator(...)` retains its signature for
Ninja's parameter inspection, supplies route arguments as path values, supports sync and async
handlers, and projects the result through the standard `ModwireSiren` composition root.

## Development and release

Run `uv sync --all-groups` and `make verify`. Releases use strict SemVer tags and PyPI Trusted
Publishing configured for repository `modwire/modwire-siren`, workflow `release.yml`, and environment
`pypi`. Create and push the tag before publishing its GitHub Release; that release drives the shared
build, attaches the verified distributions, and then publishes the same files to PyPI.

```sh
git tag -a v1.0.1 -m "v1.0.1"
git push origin v1.0.1
gh release create v1.0.1 --verify-tag --generate-notes --title v1.0.1
```
