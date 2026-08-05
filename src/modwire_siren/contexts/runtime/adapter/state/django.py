import json
from collections.abc import Callable

from pydantic import model_validator

from modwire_siren.contexts.shared import BaseState, ModwireSirenError

from ..contracts import SirenCapabilityPolicy
from ..values import SirenAccept, SirenAdapterPolicy, SirenAdapterRequest
from .adapter import SirenAdapter


class SirenDjangoMiddleware(BaseState):
    """Render negotiated Django Ninja/Ninja Extra JSON responses as Siren.

    Configure this callable as Django middleware with an application-owned `SirenCapabilityPolicy`
    or a callable returning `SirenAdapterPolicy`.
    It calls the wrapped operation exactly once and transforms only matched JSON-compatible or
    content-free responses. Unmatched, non-JSON, streaming, redirect, 304, and already-Siren responses
    pass through without projection, as do all requests that do not select Siren. Negotiation honors
    quality, specificity, wildcards, and case-insensitive media types; missing or wildcard-only Accept
    values retain JSON because neither explicitly prefers Siren. Negotiable JSON, Siren, and 304
    responses vary on Accept even when the original response object is returned.
    Unmatched errors also pass through: the bridge does not infer API ownership from URL prefixes.

    Transformed responses retain cookies and semantic or security headers, and discard validators,
    digests, encodings, ranges, and framing tied to the source JSON bytes. Place Django's
    ConditionalGetMiddleware before this middleware so it evaluates the final Siren representation on
    the response path; a downstream 304 remains untouched because its representation body is unavailable.

    Django middleware supports negotiation on the source routes that Django actually dispatches.
    Configure identical source and public paths; an independent public mount requires real framework
    routes and is rejected here because matching after execution cannot make it operational safely.
    """

    get_response: Callable[[object], object]
    adapter: SirenAdapter
    policy: SirenCapabilityPolicy | Callable[..., SirenAdapterPolicy]

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
        if match is None:
            return response
        from django.utils.cache import patch_vary_headers

        if response.status_code == 304:
            patch_vary_headers(response, ("Accept",))
            return response
        if 300 <= response.status_code < 400:
            return response
        if getattr(response, "streaming", False):
            return response
        content_type = response.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type == "application/vnd.siren+json":
            patch_vary_headers(response, ("Accept",))
            return response
        content = bytes(response.content)
        if content and content_type != "application/json" and not content_type.endswith("+json"):
            return response
        patch_vary_headers(response, ("Accept",))
        accept = request.headers.get("Accept", "")
        if not SirenAccept(value=accept).selects_siren():
            return response
        result = json.loads(content) if content else None
        if isinstance(self.policy, SirenCapabilityPolicy):
            selected = self.policy.select(match.operation_id, response.status_code, request, result)
        else:
            selected = self.policy(match.operation_id, response.status_code, request, result)
        if not isinstance(selected, SirenAdapterPolicy):
            raise ModwireSirenError("Siren capability policy must return SirenAdapterPolicy")
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
