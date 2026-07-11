# modwire-siren

Typed Siren documents projected from OpenAPI without application-owned route maps.

Every external boundary is behind a package interface: catalog, href resolution, field policy,
field creation, link creation, resource hrefs, and serialization. `ModwireSirenFactory` is the
standard composition root; `ModwireSiren` is the small public façade.

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
Publishing configured for repository `9orky/modwire-siren`, workflow `release.yml`, and environment
`pypi`.
