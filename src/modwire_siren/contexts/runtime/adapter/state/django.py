import json
from collections.abc import Callable

from modwire_siren.contexts.shared import BaseState

from ..contracts import SirenCapabilityPolicy
from ..values import SirenAdapterRequest
from .adapter import SirenAdapter


class SirenDjangoMiddleware(BaseState):
    """Render negotiated Django Ninja/Ninja Extra JSON responses as Siren.

    Configure this callable as Django middleware with an application-owned `SirenCapabilityPolicy`.
    It calls the wrapped operation exactly once. Requests that do not accept the official Siren
    media type receive the original Django response unchanged.
    """

    get_response: Callable[[object], object]
    adapter: SirenAdapter
    policy: SirenCapabilityPolicy

    def __call__(self, request: object) -> object:
        response = self.get_response(request)
        accept = request.headers.get("Accept", "")
        accepted = tuple(part.split(";", 1)[0].strip().lower() for part in accept.split(","))
        if "application/vnd.siren+json" not in accepted:
            return response
        content = bytes(response.content)
        result = json.loads(content) if content else None
        match = self.adapter.match(request.method, request.path)
        operation_id = match.operation_id if match is not None else None
        selected = self.policy.select(operation_id, response.status_code, request, result)
        content_type = None
        if content:
            content_type = response.get("Content-Type", "").split(";", 1)[0].strip() or None
        query = tuple((name, value) for name in request.GET for value in request.GET.getlist(name))
        projected = self.adapter.respond(SirenAdapterRequest(
            operation_id=operation_id,
            method=request.method,
            path=request.path,
            status=response.status_code,
            result=result,
            base_url=request.build_absolute_uri("/").rstrip("/"),
            request_url=request.build_absolute_uri(),
            media_type=content_type,
            path_values=match.path_values if match is not None else {},
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
