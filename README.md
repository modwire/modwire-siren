# modwire-siren

`modwire-siren` compiles a complete OpenAPI 3.1 document into a reusable Siren engine. At request
time, the engine turns application data and permissions into a Siren response with concrete links
and authorized actions.

Requires Python 3.12 or later.

## Install

```bash
python -m pip install modwire-siren
```

For local development, install `uv` and use the locked environment:

```bash
UV_CACHE_DIR=.dump/uv-cache uv sync --locked --all-groups
make verify
```

Version 2 is a breaking rewrite. See [MIGRATION.md](MIGRATION.md) when upgrading from version 1.

<!-- generated:public-api:start -->
## Usage

This section is generated from the docstrings of the supported root imports. Run `make docs` after changing a public API example or its guidance.

### `siren_adapter`

Compile a framework-neutral boundary for operation-aware Siren HTTP responses.

Call this once after framework routes are registered. The adapter compiles OpenAPI once and
retains a route catalogue mapping both the framework's source mount and the public Siren mount
to operation IDs. Consumers neither inspect the engine graph nor parse OpenAPI.

```python
from modwire_siren import SirenAdapterPolicy, SirenAdapterRequest, siren_adapter

adapter = siren_adapter(api.get_openapi_schema(), source_path="/api", public_path="/siren")
response = adapter.respond(SirenAdapterRequest(
    operation_id="get_article",
    status=200,
    result={"article_id": "42", "title": "Adapter boundaries"},
    base_url="https://api.example.com",
    path_values={"article_id": "42"},
    policy=SirenAdapterPolicy(capabilities=frozenset({"get_article", "update_article"})),
))

assert response.media_type == "application/vnd.siren+json"
```

The result must come from an operation the application has already executed; `respond()` never
dispatches application code. Pass `operation_id` directly when the framework exposes it, or pass
`method` and `path` for catalogue resolution. Capability sets and ambiguous object semantics are
explicit `SirenAdapterPolicy` inputs and are never inferred from OpenAPI or identifier fields.

For Django Ninja and Ninja Extra, wrap the normal Django response callable with
`SirenDjangoMiddleware`. The bridge imports Django only when rendering a negotiated Siren response,
preserves non-content headers and cookies, and returns the original response object when Siren is
not selected. Its required `SirenCapabilityPolicy` is application code:

```python
from modwire_siren import SirenAdapterPolicy, SirenDjangoMiddleware

class Capabilities:
    def select(self, operation_id, status, request, result):
        permitted = frozenset({operation_id}) if operation_id is not None else frozenset()
        return SirenAdapterPolicy(capabilities=permitted)

middleware = SirenDjangoMiddleware(
    get_response=django_handler,
    adapter=adapter,
    policy=Capabilities(),
)
```

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
                                "required": ["metadata"],
                                "properties": {
                                    "title": {"type": "string"},
                                    "metadata": {
                                        "type": "object",
                                        "properties": {"source": {"type": "string"}},
                                    },
                                },
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

payload = document.model_dump(by_alias=True, mode="json", exclude_none=True)

assert payload["actions"][0] == {
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

#### Action field support matrix

Path parameters substitute into action URLs and never become fields. Query parameters and
properties of an `application/json` object body become fields:

| OpenAPI schema | Siren field type |
| --- | --- |
| `string`, including `uuid` | `text` |
| formatted `string` | matching Siren field type |
| `integer` or `number` | `number` |
| `boolean` | `checkbox` |
| flat primitive array or repeated query parameter | `text` |
| scalar `enum` | `radio` with selectable values |
| flat array with an item `enum` | `checkbox` with selectable values |
| object, map, or nested array | delegated; no synthetic field |
| header or cookie parameter | delegated; no synthetic field |
| one non-JSON request media type | delegated action with that media type |

`email`, `uri`, `date`, `date-time`, and `time` map to `email`, `url`, `date`,
`datetime-local`, and `time`, respectively.

Required and nullable controls compile as ordinary standard Siren fields: validation remains
server-enforced because official Siren has no `required` or `nullable` members. A flat array
has one named `text` field; the OpenAPI serialization contract remains authoritative for
submission. `allOf` scalar fragments and a `oneOf` or `anyOf` containing one scalar plus
`null` are accepted when they normalize unambiguously.

Structured values, header and cookie parameters, and one non-JSON request body are delegated
to the API contract and client transport; official Siren has no standard members for their
paths, serialization, or placement. Multiple non-JSON media types, ambiguous compositions,
unsupported string formats, and `HEAD`, `OPTIONS`, or `TRACE` operations are rejected during
this startup call.

#### Adapter-facing operation inputs

Use `engine.operation_input(operation_id)` when an adapter needs the compiled request contract.
It returns the selected media type, the fully resolved request-body `definition`, the names in
`official_fields`, and separate `delegated_inputs` for structured query values, headers,
cookies, and bodies. Each delegated input retains its location, required state, media type,
normalized parameter serialization controls, and resolved definition, so an adapter does not
need to parse OpenAPI again.

```python
operation_input = engine.operation_input("rename_record")

payload = {"title": "New title"}
if operation_input is not None:
    metadata = next(value for value in operation_input.delegated_inputs if value.name == "metadata")
    if metadata.location == "body" and metadata.required:
        payload[metadata.name] = {"source": "browser"}

transport.request("PATCH", "/records/42", json=payload)
```

This metadata is separate from projection. `engine.project(context)` continues to produce an
extension-free Siren document containing only official fields.

Call `audit(openapi)` first when a consumer needs a deterministic list of every current
incompatibility before using this strict fail-fast entry point.

#### Explicit title metadata

The root document uses `info.title`, and exposes `info.version` as the official Siren
`properties.version` value. An operation's `summary` becomes its action title. Resource titles
come only from explicitly connected successful response schemas: an object schema on the exact
entity route names an entity, while an array schema on the exact collection route names its
collection and its item schema names embedded items and entities. Self and root collection
links reuse those compiled titles.

```yaml
info:
  title: Example Service
  version: 4.0.0
paths:
  /articles/{article_id}:
    get:
      operationId: get_article
      summary: Read article
      responses:
        "200":
          description: Article
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Article"
components:
  schemas:
    Article:
      type: object
      title: Article
```

`SirenContext.title`, `SirenResponseContext.title`, and `SirenRelationship.title` override the
relevant compiled default. Missing titles remain absent: the engine does not humanize operation
IDs, guess labels from URLs, or apply language-specific inflection. When operations declare
different schema titles, the exact GET representation takes precedence, followed by other
operations in OpenAPI declaration order.

#### Framework integration is one startup call

Give the framework-generated document directly to `siren()` after routes are registered:

```python
engine = siren(app.openapi())  # FastAPI
engine = siren(api.get_openapi_schema())  # Django Ninja / Django Ninja Extra
```

#### HTTP response contract

`engine.project(context)` returns a `SirenDocument`, not a dictionary. Serialize it with
`document.model_dump(by_alias=True, mode="json", exclude_none=True)` and send that payload as
`application/vnd.siren+json`. The document contains only official Siren members; action fields
never include the non-standard `required` member.

#### Operation-aware response projection

When an adapter knows the executed operation and HTTP status, pass a `SirenResponseContext`
to `engine.project_response(...)`. The engine selects the compiled response status, media
type, and resolved schema. Arrays become collection documents, objects returned from an
entity's exact route become entity documents, content-free responses become `empty` documents,
and statuses from 400 onward become `error` documents whose properties preserve the status and
structured result.

```python
from modwire_siren import SirenResponseContext

document = engine.project_response(SirenResponseContext(
    operation_id="get_record",
    status=200,
    result={"record_id": "42", "title": "Architecture"},
    base_url="https://api.example.com",
))
```

An object response from a collection, root, or entity-owned subcommand is semantically
ambiguous: set its response context `representation` to `"entity"` or `"command"`. No
identifier property name is inferred; compiled route parameters and explicit path values
resolve entity links.

Set `source_path` to the OpenAPI route prefix and `public_path` to the independently
mounted Siren prefix. Both prefixes are segment-aware and normalized without a trailing
slash. Every OpenAPI path must belong to `source_path`.

### `audit`

Inspect a valid OpenAPI document against the current official-Siren support boundary.

Call this during startup before `siren(openapi)` when a consumer needs every currently
unsupported construct at once. The report exposes typed findings and `render()` for terminal
or CI output; `siren(openapi)` remains the strict fail-fast compilation entry point.

### `SirenResponseContext`

Supply an executed OpenAPI operation and result for operation-aware projection.

The compiled response status, media type, and schema determine whether the result is empty,
an object, or an array. Array responses project as collections and object responses from an
entity's exact route project as entities. Set `representation` to `"entity"` or `"command"`
when an object response from a collection, root, or entity-owned subcommand is ambiguous.
`title` overrides the compiled resource or operation title for the projected result.

### `SirenRelationship`

Describe a runtime relationship to another OpenAPI resource.

A relationship projects as a navigational link by default. Set `embedded` when the related
resource values should be included as a Siren embedded representation instead. `title`
overrides the compiled resource title for this link or embedded representation.

### `SirenOperationInput`

Expose normalized input metadata for one compiled OpenAPI operation.

`official_fields` names the values emitted as standard Siren action fields.
`delegated_inputs` retains structured query values, headers, cookies, and body values for an
adapter or transport. `definition` is the normalized request-body schema when one is declared.

### `SirenLink`

Describe a navigational Siren link.

### `SirenFieldValue`

Describe a selectable Siren action field value.

### `SirenField`

Describe an official Siren action field.

### `SirenEmbeddedRepresentation`

Represent a Siren sub-entity embedded in full.

### `SirenEmbeddedLink`

Represent a Siren sub-entity linked by URI.

### `SirenDocument`

Represent an official Siren entity document.

Project an engine request into this immutable public value, then serialize it with
`model_dump(by_alias=True, mode="json", exclude_none=True)` for an
`application/vnd.siren+json` response. Navigation belongs in `links`; embedded sub-entities
belong in `entities`.

### `SirenDjangoMiddleware`

Render negotiated Django Ninja/Ninja Extra JSON responses as Siren.

Configure this callable as Django middleware with an application-owned `SirenCapabilityPolicy`.
It calls the wrapped operation exactly once. Requests that do not accept the official Siren
media type receive the original Django response unchanged.

### `SirenDelegatedInput`

Describe a normalized OpenAPI input delegated to an adapter or transport.

Parameter serialization defaults are materialized in `style`, `explode`, and
`allow_reserved`; body inputs instead carry their selected `media_type`.

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
| `title` | Explicit document title overriding compiled OpenAPI metadata. |
| `value` | Entity or collection properties and entity path parameters. |
| `items` | Entity mappings for a collection. |
| `item_capabilities` | Optional permitted operation IDs for each collection item. |
| `relationships` | Linked or embedded related resources for this document. |
| `path_values` | Missing path parameters, such as a parent resource ID or a root command target. |
| `query` | Ordered query pairs for self and action links. |
| `capabilities` | Permitted OpenAPI `operationId` values. |

### `SirenCompatibilityReport`

Expose deterministic OpenAPI-to-Siren compatibility findings.

### `SirenCompatibilityFinding`

Describe one OpenAPI construct outside the current official-Siren boundary.

### `SirenCapabilityPolicy`

Select explicit application capabilities and projection semantics for one response.

### `SirenAdapterResponse`

Represent an HTTP-ready official Siren response without framework dependencies.

### `SirenAdapterRequest`

Describe one already-executed HTTP operation for Siren projection.

Pass the framework's executed `operation_id` when it is available. Otherwise provide `method`
and `path` so the adapter can resolve the operation from its startup-compiled route catalogue.
`result` is the already-produced application value: the adapter never redispatches the operation.

### `SirenAdapterPolicy`

Declare application-owned projection semantics and permitted capabilities.

Adapters never infer permissions or representation semantics from OpenAPI or result identifiers.
Supply this value directly to a framework-neutral request, or return it from a framework bridge's
capability policy.

### `SirenAdapterMatch`

!!! abstract "Usage Documentation"
    [Models](../concepts/models.md)

A base class for creating Pydantic models.

Attributes:
    __class_vars__: The names of the class variables defined on the model.
    __private_attributes__: Metadata about the private attributes of the model.
    __signature__: The synthesized `__init__` [`Signature`][inspect.Signature] of the model.

    __pydantic_complete__: Whether model building is completed, or if there are still undefined fields.
    __pydantic_core_schema__: The core schema of the model.
    __pydantic_custom_init__: Whether the model has a custom `__init__` function.
    __pydantic_decorators__: Metadata containing the decorators defined on the model.
        This replaces `Model.__validators__` and `Model.__root_validators__` from Pydantic V1.
    __pydantic_generic_metadata__: A dictionary containing metadata about generic Pydantic models.
        The `origin` and `args` items map to the [`__origin__`][genericalias.__origin__]
        and [`__args__`][genericalias.__args__] attributes of [generic aliases][types-genericalias],
        and the `parameter` item maps to the `__parameter__` attribute of generic classes.
    __pydantic_parent_namespace__: Parent namespace of the model, used for automatic rebuilding of models.
    __pydantic_post_init__: The name of the post-init method for the model, if defined.
    __pydantic_root_model__: Whether the model is a [`RootModel`][pydantic.root_model.RootModel].
    __pydantic_serializer__: The `pydantic-core` `SchemaSerializer` used to dump instances of the model.
    __pydantic_validator__: The `pydantic-core` `SchemaValidator` used to validate instances of the model.

    __pydantic_fields__: A dictionary of field names and their corresponding [`FieldInfo`][pydantic.fields.FieldInfo] objects.
    __pydantic_computed_fields__: A dictionary of computed field names and their corresponding [`ComputedFieldInfo`][pydantic.fields.ComputedFieldInfo] objects.

    __pydantic_extra__: A dictionary containing extra values, if [`extra`][pydantic.config.ConfigDict.extra]
        is set to `'allow'`.
    __pydantic_fields_set__: The names of fields explicitly set during instantiation.
    __pydantic_private__: Values of private attributes set on the model instance.

### `SirenAdapter`

Project already-executed framework results through a startup-compiled Siren engine.

Use `match()` when a framework exposes only its HTTP method and path. Use `respond()` after the
application operation has executed exactly once. The adapter preserves response headers other
than content framing and returns an HTTP-ready payload with the official Siren media type.

### `SirenAction`

Describe an available Siren action.

### `ModwireSirenError`

Indicate a Modwire Siren operation failure.

## Public API

The supported root imports below are generated from `modwire_siren.__all__`.

| Symbol | Purpose | Primary API |
| --- | --- | --- |
| `ModwireSirenError` | Indicate a Modwire Siren operation failure. | — |
| `SirenAction` | Describe an available Siren action. | — |
| `SirenAdapter` | Project already-executed framework results through a startup-compiled Siren engine. | `match(method: <class 'str'>, path: <class 'str'>) -> modwire_siren.contexts.runtime.adapter.values.match.SirenAdapterMatch | None`<br>`respond(request: <class 'modwire_siren.contexts.runtime.adapter.values.request.SirenAdapterRequest'>) -> <class 'modwire_siren.contexts.runtime.adapter.values.response.SirenAdapterResponse'>`<br>`error(request: <class 'modwire_siren.contexts.runtime.adapter.values.request.SirenAdapterRequest'>) -> <class 'modwire_siren.contexts.runtime.document.values.document.SirenDocument'>` |
| `SirenAdapterMatch` | !!! abstract "Usage Documentation" | — |
| `SirenAdapterPolicy` | Declare application-owned projection semantics and permitted capabilities. | — |
| `SirenAdapterRequest` | Describe one already-executed HTTP operation for Siren projection. | — |
| `SirenAdapterResponse` | Represent an HTTP-ready official Siren response without framework dependencies. | — |
| `SirenCapabilityPolicy` | Select explicit application capabilities and projection semantics for one response. | `select(operation_id: str | None, status: <class 'int'>, request: <class 'object'>, result: JsonValue) -> <class 'modwire_siren.contexts.runtime.adapter.values.policy.SirenAdapterPolicy'>` |
| `SirenCompatibilityFinding` | Describe one OpenAPI construct outside the current official-Siren boundary. | — |
| `SirenCompatibilityReport` | Expose deterministic OpenAPI-to-Siren compatibility findings. | `compatible: <class 'bool'>`<br>`render() -> <class 'str'>` |
| `SirenContext` | Supply runtime state used to project a Siren document. | — |
| `SirenDelegatedInput` | Describe a normalized OpenAPI input delegated to an adapter or transport. | — |
| `SirenDjangoMiddleware` | Render negotiated Django Ninja/Ninja Extra JSON responses as Siren. | — |
| `SirenDocument` | Represent an official Siren entity document. | — |
| `SirenEmbeddedLink` | Represent a Siren sub-entity linked by URI. | — |
| `SirenEmbeddedRepresentation` | Represent a Siren sub-entity embedded in full. | — |
| `SirenField` | Describe an official Siren action field. | — |
| `SirenFieldValue` | Describe a selectable Siren action field value. | — |
| `SirenLink` | Describe a navigational Siren link. | — |
| `SirenOperationInput` | Expose normalized input metadata for one compiled OpenAPI operation. | — |
| `SirenRelationship` | Describe a runtime relationship to another OpenAPI resource. | — |
| `SirenResponseContext` | Supply an executed OpenAPI operation and result for operation-aware projection. | — |
| `audit` | Inspect a valid OpenAPI document against the current official-Siren support boundary. | — |
| `siren` | Compile a complete OpenAPI 3.1 document into a reusable Siren engine. | — |
| `siren_adapter` | Compile a framework-neutral boundary for operation-aware Siren HTTP responses. | — |
<!-- generated:public-api:end -->
