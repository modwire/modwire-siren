from collections.abc import Mapping
from typing import Any

from ...contracts.collection import SirenCollectionRequest
from ...contracts.entity import SirenEmbeddedEntity, SirenEntityRequest
from ...contracts.related_link import RelatedLinkInput
from .adapter import NinjaExtraSirenResponseAdapter
from .projector import RequestAwareSirenProjectorFactory, SirenProjector
from .response import EMPTY_HEADERS, EMPTY_VALUES, NinjaExtraSirenResponse
from .serializer import DEFAULT_PROPERTY_SERIALIZER, SirenPropertySerializer


class NinjaExtraSirenController:

    def __init__(
        self,
        siren: SirenProjector,
        *,
        property_serializer: SirenPropertySerializer = DEFAULT_PROPERTY_SERIALIZER,
    ):
        self._siren = siren
        self._properties = property_serializer
        self._siren_responses = NinjaExtraSirenResponseAdapter(siren, property_serializer=property_serializer)

    @classmethod
    def for_request(
        cls,
        *,
        siren_factory: RequestAwareSirenProjectorFactory,
        request: Any,
        property_serializer: SirenPropertySerializer = DEFAULT_PROPERTY_SERIALIZER,
    ):
        siren = siren_factory.for_request(request)
        return cls(siren, property_serializer=property_serializer)

    def siren_document(
        self,
        resource_name: str,
        properties: Any,
        operation_ids: tuple[str, ...],
        path_values: Mapping[str, Any],
        entities: tuple[SirenEmbeddedEntity, ...] = (),
        related_links: tuple[RelatedLinkInput, ...] = (),
    ) -> dict[str, Any]:
        serialized = self._properties.serialize(properties)
        return self._siren.document(
            SirenEntityRequest(
                resource_name=resource_name,
                properties=dict(serialized),
                operation_ids=operation_ids,
                path_values=dict(path_values),
                entities=entities,
                related_links=related_links,
            )
        )

    def siren_response(
        self,
        resource_name: str,
        properties: Mapping[str, Any],
        *,
        operation_ids: tuple[str, ...],
        path_values: Mapping[str, Any] = EMPTY_VALUES,
        entities: tuple[SirenEmbeddedEntity, ...] = (),
        related_links: tuple[RelatedLinkInput, ...] = (),
        status_code: int = 200,
        headers: Mapping[str, str] = EMPTY_HEADERS,
    ) -> NinjaExtraSirenResponse:
        return self._siren_responses.entity(
            resource_name,
            properties,
            operations=operation_ids,
            path_values=path_values,
            entities=entities,
            related_links=related_links,
            status_code=status_code,
            headers=headers,
        )

    def siren_collection_response(
        self,
        request: SirenCollectionRequest,
        *,
        status_code: int = 200,
        headers: Mapping[str, str] = EMPTY_HEADERS,
    ) -> NinjaExtraSirenResponse:
        return self._siren_responses.collection(request, status_code=status_code, headers=headers)

    @property
    def siren_responses(self) -> NinjaExtraSirenResponseAdapter:
        return self._siren_responses
