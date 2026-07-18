from collections.abc import Mapping
from typing import Any

from ...contracts.entity import SirenEmbeddedEntity, SirenEntityRequest
from ...facade import ModwireSiren
from ...standards import SirenMediaType
from .response import EMPTY_HEADERS, EMPTY_VALUES, NinjaExtraSirenResponse


class NinjaExtraSirenResponseAdapter:
    """Build framework-light response payloads for Ninja Extra controllers."""

    def __init__(self, siren: ModwireSiren):
        self._siren = siren

    def entity(
        self,
        resource_name: str,
        properties: Mapping[str, Any],
        *,
        operations: tuple[str, ...],
        path_values: Mapping[str, Any] = EMPTY_VALUES,
        entities: tuple[SirenEmbeddedEntity, ...] = (),
        status_code: int = 200,
        headers: Mapping[str, str] = EMPTY_HEADERS,
    ) -> NinjaExtraSirenResponse:
        if status_code == 204:
            raise ValueError("Siren entity responses cannot use 204 No Content; call no_content()")
        document = self._siren.document(
            SirenEntityRequest(
                resource_name=resource_name,
                properties=dict(properties),
                operation_ids=operations,
                path_values=dict(path_values),
                entities=entities,
            )
        )
        return self._response(
            document,
            status_code=status_code,
            headers=headers,
            content_type=SirenMediaType.ENTITY,
        )

    def problem(
        self,
        problem: Mapping[str, Any],
        *,
        status_code: int,
        headers: Mapping[str, str] = EMPTY_HEADERS,
    ) -> NinjaExtraSirenResponse:
        if status_code == 204:
            raise ValueError("Problem responses cannot use 204 No Content")
        body_status = problem.get("status")
        if body_status is not None and body_status != status_code:
            raise ValueError("Problem document status must match response status_code")
        return self._response(
            dict(problem),
            status_code=status_code,
            headers=headers,
            content_type=SirenMediaType.PROBLEM,
        )

    def no_content(self, *, headers: Mapping[str, str] = EMPTY_HEADERS) -> NinjaExtraSirenResponse:
        return self._response(None, status_code=204, headers=headers, content_type=None)

    @staticmethod
    def _response(
        body: dict[str, Any] | None,
        *,
        status_code: int,
        headers: Mapping[str, str],
        content_type: str | None,
    ) -> NinjaExtraSirenResponse:
        if any(name.lower() == "content-type" for name in headers):
            raise ValueError("Pass response media type through content_type, not headers")
        return NinjaExtraSirenResponse(
            body=body,
            status_code=status_code,
            headers=dict(headers),
            content_type=content_type,
        )
