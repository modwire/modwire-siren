from collections.abc import Mapping
from typing import Any

from ..contexts.runtime.adapter import SirenAdapter
from ..contexts.runtime.adapter.values import SirenAdapterRoute
from ..contexts.shared import ModwireSirenError
from .siren import siren


def siren_adapter(
    openapi: Mapping[str, Any], *, source_path: str = "/", public_path: str = "/"
) -> SirenAdapter:
    """Compile a framework-neutral boundary for operation-aware Siren HTTP responses.

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
    """

    try:
        engine = siren(openapi, source_path=source_path, public_path=public_path)
        source = source_path.rstrip("/") or "/"
        public = public_path.rstrip("/") or "/"
        routes = []
        for operation in engine.api.operations:
            public_route = operation.route.path
            if public == "/":
                suffix = public_route
            elif public_route == public:
                suffix = "/"
            else:
                suffix = public_route[len(public):]
            source_route = suffix if source == "/" else source + ("" if suffix == "/" else suffix)
            routes.append(SirenAdapterRoute(
                source_path=source_route,
                public_path=public_route,
                method=operation.method,
                operation_id=operation.name,
            ))
        return SirenAdapter(engine=engine, routes=tuple(routes))
    except Exception as error:
        raise ModwireSirenError("Invalid or unsupported Siren adapter contract") from error
