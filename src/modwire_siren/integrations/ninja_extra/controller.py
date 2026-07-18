from collections.abc import Mapping
from typing import Any

from ...contracts.entity import SirenEmbeddedEntity, SirenEntityRequest
from ...facade import ModwireSiren
from .adapter import NinjaExtraSirenResponseAdapter
from .response import NinjaExtraSirenResponse


class NinjaExtraSirenController:
    """Framework-light base for Ninja Extra controllers that emit Siren documents."""

    def __init__(self, siren: ModwireSiren):
        self._siren = siren
        self._siren_responses = NinjaExtraSirenResponseAdapter(siren)

    def siren_document(
        self,
        resource_name: str,
        properties: Mapping[str, Any],
        operation_ids: tuple[str, ...],
        path_values: Mapping[str, Any],
        entities: tuple[SirenEmbeddedEntity, ...] = (),
    ) -> dict[str, Any]:
        return self._siren.document(
            SirenEntityRequest(
                resource_name=resource_name,
                properties=dict(properties),
                operation_ids=operation_ids,
                path_values=dict(path_values),
                entities=entities,
            )
        )

    def siren_response(
        self,
        resource_name: str,
        properties: Mapping[str, Any] | None,
        *,
        operation_ids: tuple[str, ...],
        path_values: Mapping[str, Any] | None = None,
        entities: tuple[SirenEmbeddedEntity, ...] = (),
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> NinjaExtraSirenResponse:
        return self._siren_responses.entity(
            resource_name,
            properties,
            operations=operation_ids,
            path_values=path_values,
            entities=entities,
            status_code=status_code,
            headers=headers,
        )

    @property
    def siren_responses(self) -> NinjaExtraSirenResponseAdapter:
        return self._siren_responses
