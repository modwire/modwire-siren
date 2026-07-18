from collections.abc import Mapping
from typing import Any

from ...contracts.collection import SirenCollectionRequest
from ...contracts.entity import SirenEmbeddedEntity, SirenEntityRequest
from ...facade import ModwireSiren
from ...standards import SirenMediaType
from .response import EMPTY_HEADERS, EMPTY_VALUES, NinjaExtraSirenResponse, NinjaExtraSirenResponseFactory


class NinjaExtraSirenResponseAdapter:
    """Build framework-light response payloads for Ninja Extra controllers."""

    def __init__(self, siren: ModwireSiren):
        self._siren = siren
        self._responses = NinjaExtraSirenResponseFactory()

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
        return self._responses.create(
            document,
            status_code=status_code,
            headers=headers,
            content_type=SirenMediaType.ENTITY,
        )

    def collection(
        self,
        request: SirenCollectionRequest,
        *,
        status_code: int = 200,
        headers: Mapping[str, str] = EMPTY_HEADERS,
    ) -> NinjaExtraSirenResponse:
        if status_code == 204:
            raise ValueError("Siren collection responses cannot use 204 No Content; call no_content()")
        return self._responses.create(
            self._siren.collection(request),
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
        return self._responses.create(
            dict(problem),
            status_code=status_code,
            headers=headers,
            content_type=SirenMediaType.PROBLEM,
        )

    def no_content(self, *, headers: Mapping[str, str] = EMPTY_HEADERS) -> NinjaExtraSirenResponse:
        return self._responses.create(None, status_code=204, headers=headers, content_type=None)
