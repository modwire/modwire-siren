# modwire-siren

Typed Siren documents projected from one OpenAPI API graph. There is no Siren route map and no
per-controller Siren declaration: either the API names its resources coherently or composition
fails before serving a misleading hypermedia document.

## Contents

- [What Siren is](#what-siren-is)
- [Install](#install)
- [What this package adds](#what-this-package-adds)
- [Approved UI profile](#approved-ui-profile)
- [Following advertised controls](#following-advertised-controls)
- [Public API](#public-api)
- [OpenAPI contract](#openapi-contract)
- [Collection projection](#collection-projection)
- [API graph contract](#api-graph-contract)
- [Development and release](#development-and-release)

## Install

```sh
pip install modwire-siren
```

The engine has no framework dependency. OpenAPI is its structural input; framework integration is
only responsible for obtaining that final OpenAPI document and mapping rendered HTTP responses.

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
`modwire-siren` reads routes, operations, and request schemas from that one document, derives the
resource catalog from the route grammar, then projects runtime values into entity and collection
documents. Applications do not maintain a second route map or resource registry.

The route graph determines candidate actions. Authorization and resource state determine which of
those candidates are advertised for a particular response; that decision remains application data,
not route metadata.

## Approved UI profile

The owner-approved [Modwire Siren UI Profile](docs/siren-ui-profile/README.md) defines a Siren-native,
framework-independent vocabulary for nested interfaces, action forms, semantic component selection,
and predictable state transitions. This package implements its producer, validation, discovery, and
enhancement contract. The packaged JSON Schema is the only vocabulary and type authority. Python
applies its progressive defaults to plain JSON data and rejects dangling properties, relations,
actions, fields, and regions through one structured validation error contract.

The supported Python profile revision is `1.0-draft`, identified by
`https://raw.githubusercontent.com/modwire/modwire-siren/main/docs/siren-ui-profile/README.md`. Profiled responses advertise both the required
profile link and the media type parameter. `SirenProfile.media_type` exposes the exact response
`Content-Type` for a framework adapter.

OpenAPI resources opt in with `x-siren-ui-profile`. The extension contains the complete schema-valid
metadata document. Runtime `operation_ids` remain the authorization authority: unavailable actions
and their presentation metadata are removed together before reference validation and serialization.

```yaml
paths:
  /records/{record_slug}:
    x-siren-resource:
      name: record
      class: record
      identifier: slug
      path-parameters: {record_slug: slug}
      relations: {}
    x-siren-ui-profile:
      profile: https://raw.githubusercontent.com/modwire/modwire-siren/main/docs/siren-ui-profile/README.md
      presentation: {role: detail}
      properties:
        title: {label: Title, importance: primary}
      actions:
        revise_record:
          intent: primary
          result: {mode: replace, relations: [self], optimistic: false}
    patch:
      operationId: revise_record
      summary: Revise record
```

The [`modwire_siren.profile`](docs/siren-ui-profile/python-api.md) package exposes one profile class.
It also enhances manually assembled Siren dictionaries, so OpenAPI is an integration path rather
than a requirement:

```python
from modwire_siren.profile import SirenProfile

profile = SirenProfile()
metadata = profile.discover(document)
```

## Following advertised controls

`SirenClient` consumes links and actions without reconstructing server routes. The caller owns an
async `SirenTransport` and its lifecycle, so the package remains independent of HTTP libraries:

```python
from modwire_siren import SirenClient

client = SirenClient("https://api.example.com/", transport)
root = await client.root()
records = await client.follow(root, "records")
record = await client.collection_item(records, "architecture")
updated = await client.execute(record, "revise_record", {"title": "Architecture"})
```

Relative targets are resolved against the configured root and must remain on the same origin.
Missing or malformed affordances raise `SirenClientError`; non-success responses preserve their
status and complete problem document.

## Release status

The current package surface covers the release-critical Siren producer workflow:

- entity and collection projection from OpenAPI operation/resource metadata;
- offset and custom collection pagination links;
- typed `x-siren-resource` declarations, injection, and validation;
- resource-owned sub-actions for operations below the resource path;
- dynamic operation and related-link policy hooks; and
- Django Ninja Extra response payloads for Siren, problem JSON, and 204 responses.

Remaining ecosystem work is intentionally outside this release surface: publishing the resource and
profile schemas at stable public URLs, adding editor integrations, and adding concrete adapters for
more web frameworks.

<!-- generated:public-api:start -->
## Public API

The supported root imports below are generated from `modwire_siren.__all__`.

| Symbol | Purpose | Primary API |
| --- | --- | --- |
| `CustomPagination` | Use application-provided collection pagination links. | — |
| `ModwireSiren` | Project validated entity requests into serialized Siren documents. | `document(request: <class 'modwire_siren.contracts.entity.SirenEntityRequest'>) -> dict[str, typing.Any]`<br>`collection(request: <class 'modwire_siren.contracts.collection.SirenCollectionRequest'>) -> dict[str, typing.Any]`<br>`root(*, self_href: <class 'str'>, title: <class 'str'> = '', version: <class 'str'> = '', service_desc_href: <class 'str'> = '', extra_links: tuple[collections.abc.Mapping[str, typing.Any], ...] = ()) -> dict[str, typing.Any]` |
| `ModwireSirenFactory` | Build the standard OpenAPI-backed Siren façade. | `standard(schema: dict[str, typing.Any], base_url: <class 'str'>) -> <class 'modwire_siren.facade.ModwireSiren'>`<br>`web(schema: dict[str, typing.Any], *, base_url_resolver: str | collections.abc.Callable[[typing.Any], str]) -> RequestAwareModwireSirenFactory` |
| `NinjaExtraSirenController` | Framework-light base for Ninja Extra controllers that emit Siren documents. | `for_request(*, siren_factory: <class 'modwire_siren.integrations.ninja_extra.projector.RequestAwareSirenProjectorFactory'>, request: typing.Any, property_serializer: <class 'modwire_siren.integrations.ninja_extra.serializer.SirenPropertySerializer'> = <modwire_siren.integrations.ninja_extra.serializer.DefaultSirenPropertySerializer>)`<br>`siren_document(resource_name: <class 'str'>, properties: typing.Any, operation_ids: tuple[str, ...], path_values: collections.abc.Mapping[str, typing.Any], entities: tuple[modwire_siren.contracts.entity.SirenEmbeddedEntity, ...] = (), related_links: tuple[modwire_siren.contracts.related_link.RelatedLinkInput, ...] = ()) -> dict[str, typing.Any]`<br>`siren_response(resource_name: <class 'str'>, properties: collections.abc.Mapping[str, typing.Any], *, operation_ids: tuple[str, ...], path_values: collections.abc.Mapping[str, typing.Any] = <modwire_siren.integrations.ninja_extra.response.EmptyMapping>, entities: tuple[modwire_siren.contracts.entity.SirenEmbeddedEntity, ...] = (), related_links: tuple[modwire_siren.contracts.related_link.RelatedLinkInput, ...] = (), status_code: <class 'int'> = 200, headers: collections.abc.Mapping[str, str] = <modwire_siren.integrations.ninja_extra.response.EmptyMapping>) -> <class 'modwire_siren.integrations.ninja_extra.response.NinjaExtraSirenResponse'>`<br>`siren_collection_response(request: <class 'modwire_siren.contracts.collection.SirenCollectionRequest'>, *, status_code: <class 'int'> = 200, headers: collections.abc.Mapping[str, str] = <modwire_siren.integrations.ninja_extra.response.EmptyMapping>) -> <class 'modwire_siren.integrations.ninja_extra.response.NinjaExtraSirenResponse'>`<br>`siren_responses: <class 'modwire_siren.integrations.ninja_extra.adapter.NinjaExtraSirenResponseAdapter'>` |
| `NinjaExtraSirenResponse` | Framework-light response payload for Ninja Extra adapters. | — |
| `NinjaExtraSirenResponseAdapter` | Build framework-light response payloads for Ninja Extra controllers. | `for_request(*, siren_factory: <class 'modwire_siren.integrations.ninja_extra.projector.RequestAwareSirenProjectorFactory'>, request: typing.Any, property_serializer: <class 'modwire_siren.integrations.ninja_extra.serializer.SirenPropertySerializer'> = <modwire_siren.integrations.ninja_extra.serializer.DefaultSirenPropertySerializer>) -> NinjaExtraSirenResponseAdapter`<br>`entity(resource_name: <class 'str'>, properties: typing.Any, *, operations: tuple[str, ...], path_values: collections.abc.Mapping[str, typing.Any] = <modwire_siren.integrations.ninja_extra.response.EmptyMapping>, entities: tuple[modwire_siren.contracts.entity.SirenEmbeddedEntity, ...] = (), related_links: tuple[modwire_siren.contracts.related_link.RelatedLinkInput, ...] = (), status_code: <class 'int'> = 200, headers: collections.abc.Mapping[str, str] = <modwire_siren.integrations.ninja_extra.response.EmptyMapping>) -> <class 'modwire_siren.integrations.ninja_extra.response.NinjaExtraSirenResponse'>`<br>`collection(request: <class 'modwire_siren.contracts.collection.SirenCollectionRequest'>, *, status_code: <class 'int'> = 200, headers: collections.abc.Mapping[str, str] = <modwire_siren.integrations.ninja_extra.response.EmptyMapping>) -> <class 'modwire_siren.integrations.ninja_extra.response.NinjaExtraSirenResponse'>`<br>`problem(problem: collections.abc.Mapping[str, typing.Any], *, status_code: <class 'int'>, headers: collections.abc.Mapping[str, str] = <modwire_siren.integrations.ninja_extra.response.EmptyMapping>) -> <class 'modwire_siren.integrations.ninja_extra.response.NinjaExtraSirenResponse'>`<br>`no_content(*, headers: collections.abc.Mapping[str, str] = <modwire_siren.integrations.ninja_extra.response.EmptyMapping>) -> <class 'modwire_siren.integrations.ninja_extra.response.NinjaExtraSirenResponse'>`<br>`exception(error: <class 'BaseException'>, *, title: <class 'str'> = '', status: <class 'int'> = 500, detail: <class 'str'> = '', type_: <class 'str'> = '', instance: <class 'str'> = '', headers: collections.abc.Mapping[str, str] = <modwire_siren.integrations.ninja_extra.response.EmptyMapping>) -> <class 'modwire_siren.integrations.ninja_extra.response.NinjaExtraSirenResponse'>`<br>`validation(errors: typing.Any, *, title: <class 'str'> = 'Validation error', status: <class 'int'> = 422, detail: <class 'str'> = '', type_: <class 'str'> = '', instance: <class 'str'> = '', headers: collections.abc.Mapping[str, str] = <modwire_siren.integrations.ninja_extra.response.EmptyMapping>) -> <class 'modwire_siren.integrations.ninja_extra.response.NinjaExtraSirenResponse'>` |
| `OffsetPagination` | Create standard offset pagination links for a collection. | — |
| `OpenApiError` | Report invalid or incomplete OpenAPI data used for Siren projection. | — |
| `PaginationLinkInput` | Describe one collection pagination link relative to the collection path. | — |
| `RelatedLinkInput` | Describe one application-owned related link for Siren projection. | — |
| `SirenClient` | Navigate Siren relations and execute only advertised actions. | `root() -> dict[str, typing.Any]`<br>`follow(document: Mapping[str, typing.Any], relation: str) -> dict[str, typing.Any]`<br>`execute(document: Mapping[str, typing.Any], action_name: str, payload: Mapping[str, typing.Any] | None = None) -> dict[str, typing.Any]`<br>`action(document: Mapping[str, typing.Any], action_name: str) -> Mapping[str, typing.Any]`<br>`collection_item(collection: Mapping[str, typing.Any], identifier: typing.Any, *, identifier_field: str = 'id') -> dict[str, typing.Any]` |
| `SirenClientError` | Report navigation, affordance, transport, and remote problem failures. | `as_dict() -> dict[str, typing.Any]`<br>`problem(status_code: int, document: Mapping[str, typing.Any]) -> SirenClientError` |
| `SirenCollectionRequest` | Describe resource items and controls projected into one Siren collection. | — |
| `SirenEntityDecorator` | Turn a controller method's property mapping into a Siren entity document. | — |
| `SirenEntityRequest` | Describe the resource data and allowed operations projected into one entity. | — |
| `SirenRelationSpec` | Declare one relation in an x-siren-resource extension. | — |
| `SirenResourceSpec` | Declare one x-siren-resource extension for an OpenAPI path template. | — |
| `SirenResponse` | Carry one transport response without coupling Siren to an HTTP library. | — |
| `SirenTransport` | Execute Siren requests for a client-owned transport lifecycle. | `request(method: str, href: str, payload: Mapping[str, typing.Any] | None = None) -> SirenResponse` |
| `__version__` | Installed distribution version. | — |
| `collect_siren_resources` | Collect Siren resource declarations attached to controller classes. | — |
| `inject_siren_resources` | Attach typed Siren resource declarations to an OpenAPI schema copy. | — |
| `siren_collection` | Turn a controller method's item mappings into a Siren collection response payload. | — |
| `siren_entity` | Turn a controller method's property mapping into a Siren response payload. | — |
| `siren_resource` | Attach a typed Siren resource declaration to a Ninja Extra controller class. | — |
| `validate_siren_resources` | Validate Siren resource metadata with the standard OpenAPI catalog. | — |

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
      operations:
        - preview_record
    patch:
      operationId: revise_record
      summary: Revise record
  /records/{record_slug}/preview:
    post:
      operationId: preview_record
      summary: Preview record
```

The strict `OpenApiResourceExtension` validates the extension. Unknown resources, incomplete path
mappings, absent operation IDs, and unknown schema references fail while building the catalog.
Applications can declare the same metadata without hand-writing extension dictionaries:

```python
from modwire_siren import SirenRelationSpec, SirenResourceSpec, inject_siren_resources, validate_siren_resources

schema = inject_siren_resources(
    schema,
    (
        SirenResourceSpec(
            name="record",
            path="/records/{record_slug}",
            resource_class="record",
            identifier="slug",
            path_parameters={"record_slug": "slug"},
            relations={
                "section_slug": SirenRelationSpec(rel="section", resource="section", many=False),
            },
        ),
    ),
)
validate_siren_resources(schema, ("record",))
```

Resource spec paths use OpenAPI template syntax such as `/records/{record_slug}`. Framework route
converter syntax such as `/{path:record_slug}` is rejected before injection. The base URL still
belongs to `ModwireSirenFactory.standard(schema, base_url)`; resource declarations describe schema
paths only and do not carry deployment URLs.

Resource-owned operations allow sub-actions below the resource path. Operations listed in
`x-siren-resource.operations` may be advertised for that resource even when their OpenAPI path is a
child path such as `/records/{record_slug}/preview`. Other foreign-path operations remain rejected.
Owned sub-actions must not introduce extra path placeholders beyond the resource path; projection
has only the resource path values available when it builds entity actions.

Identifiers may be named `id`, `slug`, or another field, but the identifier must be one of the
fields mapped by `path-parameters`. Route `path_values` can supply values not present in returned
properties. Path-like identifiers are URL encoded during href creation, so
`architecture/aggregate` becomes `architecture%2Faggregate`.

Static command-result resources and singleton subresources can set `singleton=True` on
`SirenResourceSpec` or `singleton: true` in `x-siren-resource`. Singleton resources can omit an
identifier field from returned properties and still emit a `self` link when route `path_values`
resolve the path. Singleton resources are not advertised from the root document by default; set
`root_visible=True` or `root-visible: true` to expose an explicit root link.

The Pydantic Siren contracts own wire aliases such as `class`, `type`, and `schema`.
`PydanticSirenSerializer` implements the `SirenSerializer` interface with one model dump; it does
not redeclare the wire schema.

## Collection projection

Collections use a separate request type but keep OpenAPI as the route and action source of truth:

```python
from modwire_siren import ModwireSirenFactory, OffsetPagination, SirenCollectionRequest

siren = ModwireSirenFactory.standard(schema, "https://api.example.com/")
document = siren.collection(
    SirenCollectionRequest(
        resource_name="record",
        items=(
            {"slug": "architecture", "title": "Architecture"},
            {"slug": "billing", "title": "Billing"},
        ),
        collection_operation_ids=("list_records", "create_record"),
        item_operation_ids=("get_record",),
        path_values={},
        pagination=OffsetPagination(limit=50, offset=0, count=2, has_next=False),
    )
)
```

The resulting Siren document has `class: ["collection", "record"]`, `properties.count`, embedded
item entities with `rel: ["item"]`, collection actions from the supplied collection operation IDs,
and item actions from the supplied item operation IDs. Offset pagination emits `self`, `first`,
`previous` when applicable, and `next` when `has_next` is true. `CustomPagination` lets
applications provide package-owned pagination link inputs while still requiring an explicit `self`
link. Collection links are built from the collection operation path plus explicit pagination link
inputs. Existing request query values can be supplied through `SirenCollectionRequest.query`; link
query values such as `offset` override only that key, preserving unrelated repeated filters such as
`tag=alpha&tag=beta`.

## Django Ninja Extra

The controller adapter does not import Django or Ninja Extra, so the core package keeps no framework
dependency. It composes directly with Ninja Extra's controller and route decorators:

```python
from ninja_extra import ControllerBase, api_controller, route
from modwire_siren import (
    ModwireSiren,
    NinjaExtraSirenController,
    RelatedLinkInput,
    collect_siren_resources,
    inject_siren_resources,
    siren_collection,
    siren_entity,
    siren_resource,
)

class RecordSirenPolicy:
    def operations_for_entity(self, request, resource_name, properties):
        operations = ["get_record"]
        if request.user.can_edit(properties):
            operations.append("revise_record")
        return tuple(operations)

    def operations_for_collection(self, request, resource_name):
        operations = ["list_records"]
        if request.user.can_create(resource_name):
            operations.append("create_record")
        return tuple(operations)

    def related_links_for_entity(self, request, resource_name, properties):
        if "owner_id" in properties:
            return (RelatedLinkInput(rel="owner", resource="user", value=properties["owner_id"]),)
        return ()

@siren_resource(
    name="record",
    path="/records/{record_slug}",
    class_="record",
    identifier="slug",
    path_parameters={"record_slug": "slug"},
    relations={},
)
@api_controller("/records")
class RecordController(ControllerBase, NinjaExtraSirenController):
    def __init__(self, records: RecordService, siren: ModwireSiren):
        NinjaExtraSirenController.__init__(self, siren)
        self.records = records

    @route.get("/{record_slug}", operation_id="get_record")
    @siren_entity(resource="record", policy=RecordSirenPolicy())
    def get_record(self, request, record_slug: str):
        return self.records.get(record_slug)

    @route.get("", operation_id="list_records")
    @siren_collection(resource="record", policy=RecordSirenPolicy(), item_operations=("get_record",))
    def list_records(self, request):
        return self.records.list()

schema = inject_siren_resources(schema, collect_siren_resources(RecordController))
```

The method returns only resource properties. `@siren_entity(...)` retains its signature for Ninja's
parameter inspection, supplies route arguments as path values, supports sync and async handlers, and
projects the result through the standard `ModwireSiren` composition root. The decorator returns a
framework-light `NinjaExtraSirenResponse` with `body`, `status_code`, `headers`, and `content_type`
fields. Framework code can map those fields onto its response object while preserving non-content
headers. `SirenEntityDecorator(...)` remains available for controllers that need the plain Siren
document dictionary instead of a response payload.

Lower-level response APIs are available when decorators do not fit:

```python
response = controller.siren_responses.entity(
    "record",
    {"slug": "architecture", "title": "Architecture"},
    operations=("get_record", "revise_record"),
)

problem = controller.siren_responses.problem(
    {"title": "Missing record", "status": 404},
    status_code=404,
)

empty = controller.siren_responses.no_content()
```

The response factory rejects duplicate `Content-Type` headers and mismatched problem statuses. A
204 response carries no body and no content type.

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
