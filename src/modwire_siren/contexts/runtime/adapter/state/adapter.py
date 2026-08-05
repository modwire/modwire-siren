from urllib.parse import unquote

from modwire_siren.contexts.shared import BaseState, ModwireSirenError

from ...document import SirenDocument, SirenLink
from ...engine import SirenEngine
from ...request import SirenResponseContext
from ..values import SirenAdapterMatch, SirenAdapterRequest, SirenAdapterResponse, SirenAdapterRoute


class SirenAdapter(BaseState):
    """Project already-executed framework results through a startup-compiled Siren engine.

    Use `match()` when a framework exposes only its HTTP method and path. Use `respond()` after the
    application operation has executed exactly once. The adapter preserves response headers other
    than content framing and returns an HTTP-ready payload with the official Siren media type.
    """

    engine: SirenEngine
    routes: tuple[SirenAdapterRoute, ...]

    def match(self, method: str, path: str) -> SirenAdapterMatch | None:
        normalized = "/" + path.strip("/") if path.strip("/") else "/"
        for route in self.routes:
            if route.method != method.upper():
                continue
            for template in (route.source_path, route.public_path):
                template_parts = template.strip("/").split("/") if template != "/" else []
                path_parts = normalized.strip("/").split("/") if normalized != "/" else []
                if len(template_parts) != len(path_parts):
                    continue
                values = {}
                matches = True
                for expected, actual in zip(template_parts, path_parts, strict=True):
                    if expected.startswith("{") and expected.endswith("}"):
                        values[expected[1:-1]] = unquote(actual)
                    elif expected != actual:
                        matches = False
                        break
                if matches:
                    return SirenAdapterMatch(operation_id=route.operation_id, path_values=values)
        return None

    def respond(self, request: SirenAdapterRequest) -> SirenAdapterResponse:
        try:
            match = None
            if request.operation_id is None and request.method is not None and request.path is not None:
                match = self.match(request.method, request.path)
            operation_id = request.operation_id or (match.operation_id if match is not None else None)
            path_values = dict(match.path_values if match is not None else {}) | dict(request.path_values)
            if operation_id is None:
                document = self.error(request)
            else:
                document = self.engine.project_response(SirenResponseContext(
                    operation_id=operation_id,
                    status=request.status,
                    result=request.result,
                    base_url=request.base_url,
                    title=request.policy.title,
                    media_type=request.media_type,
                    representation=request.policy.representation,
                    path_values=path_values,
                    query=request.query,
                    capabilities=request.policy.capabilities,
                    item_capabilities=request.policy.item_capabilities,
                    relationships=request.policy.relationships,
                ))
            headers = {
                name: value
                for name, value in request.headers.items()
                if name.lower() not in {"content-type", "content-length"}
            }
            return SirenAdapterResponse(
                status=request.status,
                payload=document.model_dump(by_alias=True, mode="json", exclude_none=True),
                headers=headers,
            )
        except Exception as error:
            raise ModwireSirenError("Siren adapter response failed") from error

    def error(self, request: SirenAdapterRequest) -> SirenDocument:
        if request.status < 400:
            raise ModwireSirenError("An unmatched successful response cannot be projected")
        properties = {"status": request.status}
        if isinstance(request.result, dict):
            properties = dict(request.result) | properties
        elif isinstance(request.result, list):
            properties["errors"] = request.result
        elif request.result is not None:
            properties["result"] = request.result
        links = ()
        if request.request_url is not None:
            links = (SirenLink(rel=("self",), title=request.policy.title, href=request.request_url),)
        return SirenDocument(
            class_=("error",),
            title=request.policy.title,
            properties=properties,
            links=links or None,
        )
