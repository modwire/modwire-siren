import json
from collections.abc import Mapping
from typing import Any

from openapi_spec_validator import validate

from .engine import SirenEngine
from .service import SirenApiService
from .sources import OpenApiSource


def siren(openapi: Mapping[str, Any], *, root_path: str = "/") -> SirenEngine:
    """Compile a complete OpenAPI 3.1 document into a reusable Siren engine.

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
    Parameters must be unchanged from the owning route: adding, removing, renaming, or reordering
    them is unsupported. Ambiguous or unsupported routes, duplicate resource names, missing
    operation IDs, and invalid OpenAPI fail compilation explicitly.

    Local `#/components/parameters`, `#/components/requestBodies`, and `#/components/schemas`
    references are resolved for actions. External and path-item references
    are unsupported. Action fields come from query parameters and JSON request-body properties;
    path parameters remain routing values. Header and cookie parameters are unsupported. If a
    request body declares content, it must include `application/json`.

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
    """
    if not isinstance(openapi, Mapping):
        raise TypeError("OpenAPI document must be a mapping")
    if not isinstance(root_path, str) or not root_path.startswith("/"):
        raise ValueError("Siren root path must start with '/'")
    try:
        document = json.loads(json.dumps(openapi))
        validate(document)
    except RecursionError as error:
        raise ValueError("OpenAPI document is invalid: cyclic reference") from error
    except Exception as error:
        raise ValueError(f"OpenAPI document is invalid: {error}") from error
    api = SirenApiService((OpenApiSource(root_path=root_path),)).build(document)
    return SirenEngine(api)
