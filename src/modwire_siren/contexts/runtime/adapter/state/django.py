import json
from collections.abc import Callable

from pydantic import model_validator

from modwire_siren.contexts.shared import BaseState, ModwireSirenError

from ..contracts import SirenCapabilityPolicy
from ..values import SirenAdapterRequest
from .adapter import SirenAdapter


class SirenDjangoMiddleware(BaseState):
    """Render negotiated Django Ninja/Ninja Extra JSON responses as Siren.

    Configure this callable as Django middleware with an application-owned `SirenCapabilityPolicy`.
    It calls the wrapped operation exactly once and transforms only matched JSON-compatible or
    content-free responses. Unmatched, non-JSON, streaming, redirect, 304, and already-Siren
    responses pass through unchanged, as do all requests that do not select Siren.
    Unmatched errors also pass through: the bridge does not infer API ownership from URL prefixes.

    Django middleware supports negotiation on the source routes that Django actually dispatches.
    Configure identical source and public paths; an independent public mount requires real framework
    routes and is rejected here because matching after execution cannot make it operational safely.
    """

    get_response: Callable[[object], object]
    adapter: SirenAdapter
    policy: SirenCapabilityPolicy

    @model_validator(mode="after")
    def validate_routes(self) -> "SirenDjangoMiddleware":
        if any(route.source_path != route.public_path for route in self.adapter.routes):
            raise ModwireSirenError(
                "Django Siren middleware requires identical source and public paths; "
                "install real framework routes for an independent public mount"
            )
        return self

    def __call__(self, request: object) -> object:
        match = self.adapter.match(request.method, request.path)
        response = self.get_response(request)
        accept = request.headers.get("Accept", "")
        accepted = tuple(part.split(";", 1)[0].strip().lower() for part in accept.split(","))
        if "application/vnd.siren+json" not in accepted:
            return response
        if match is None or 300 <= response.status_code < 400:
            return response
        if getattr(response, "streaming", False):
            return response
        content_type = response.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type == "application/vnd.siren+json":
            return response
        content = bytes(response.content)
        if content and content_type != "application/json" and not content_type.endswith("+json"):
            return response
        result = json.loads(content) if content else None
        selected = self.policy.select(match.operation_id, response.status_code, request, result)
        query = tuple((name, value) for name in request.GET for value in request.GET.getlist(name))
        projected = self.adapter.respond(SirenAdapterRequest(
            operation_id=match.operation_id,
            method=request.method,
            path=request.path,
            status=response.status_code,
            result=result,
            base_url=request.build_absolute_uri("/").rstrip("/"),
            request_url=request.build_absolute_uri(),
            media_type=content_type if content else None,
            path_values=match.path_values,
            query=query,
            headers=dict(response.items()),
            policy=selected,
        ))
        from django.http import JsonResponse

        rendered = JsonResponse(
            projected.payload,
            status=projected.status,
            content_type=projected.media_type,
            headers=dict(projected.headers),
        )
        rendered.cookies = response.cookies
        return rendered
