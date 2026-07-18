from collections.abc import Mapping
from typing import Any

from ...contracts.entity import SirenEmbeddedEntity, SirenEntityRequest
from ...facade import ModwireSiren
from ...standards import SirenMediaType
from .response import NinjaExtraSirenResponse

PROBLEM_JSON = "application/problem+json"


class NinjaExtraSirenResponseAdapter:
    """Build framework-light response payloads for Ninja Extra controllers."""

    def __init__(self, siren: ModwireSiren):
        self._siren = siren

    def entity(
        self,
        resource_name: str,
        properties: Mapping[str, Any] | None,
        *,
        operations: tuple[str, ...],
        path_values: Mapping[str, Any] | None = None,
        entities: tuple[SirenEmbeddedEntity, ...] = (),
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> NinjaExtraSirenResponse:
        if status_code == 204:
            return self.no_content(headers=headers)
        if properties is None:
            raise ValueError("Siren entity responses require properties unless status_code is 204")
        document = self._siren.document(
            SirenEntityRequest(
                resource_name=resource_name,
                properties=dict(properties),
                operation_ids=operations,
                path_values=dict(path_values or {}),
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
        status_code: int | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> NinjaExtraSirenResponse:
        resolved_status = status_code or self._problem_status(problem)
        if resolved_status == 204:
            raise ValueError("Problem responses cannot use 204 No Content")
        return self._response(
            dict(problem),
            status_code=resolved_status,
            headers=headers,
            content_type=PROBLEM_JSON,
        )

    def no_content(self, *, headers: Mapping[str, str] | None = None) -> NinjaExtraSirenResponse:
        return self._response(None, status_code=204, headers=headers, content_type=None)

    @staticmethod
    def _problem_status(problem: Mapping[str, Any]) -> int:
        status = problem.get("status", 500)
        return status if isinstance(status, int) else 500

    @staticmethod
    def _response(
        body: dict[str, Any] | None,
        *,
        status_code: int,
        headers: Mapping[str, str] | None,
        content_type: str | None,
    ) -> NinjaExtraSirenResponse:
        return NinjaExtraSirenResponse(
            body=body,
            status_code=status_code,
            headers={name: value for name, value in (headers or {}).items() if name.lower() != "content-type"},
            content_type=content_type,
        )
