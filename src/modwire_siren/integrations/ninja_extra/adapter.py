from collections.abc import Mapping
from typing import Any

from ...contracts.collection import SirenCollectionRequest
from ...contracts.entity import SirenEmbeddedEntity, SirenEntityRequest
from ...contracts.related_link import RelatedLinkInput
from ...standards import SirenMediaType
from .projector import RequestAwareSirenProjectorFactory, SirenProjector
from .response import EMPTY_HEADERS, EMPTY_VALUES, NinjaExtraSirenResponse, NinjaExtraSirenResponseFactory
from .serializer import DEFAULT_PROPERTY_SERIALIZER, SirenPropertySerializer, serialize_collection_items


class NinjaExtraSirenResponseAdapter:
    """Build framework-light response payloads for Ninja Extra controllers."""

    def __init__(
        self,
        siren: SirenProjector,
        *,
        property_serializer: SirenPropertySerializer = DEFAULT_PROPERTY_SERIALIZER,
    ):
        self._siren = siren
        self._responses = NinjaExtraSirenResponseFactory()
        self._properties = property_serializer

    @classmethod
    def for_request(
        cls,
        *,
        siren_factory: RequestAwareSirenProjectorFactory,
        request: Any,
        property_serializer: SirenPropertySerializer = DEFAULT_PROPERTY_SERIALIZER,
    ) -> "NinjaExtraSirenResponseAdapter":
        siren = siren_factory.for_request(request)
        return cls(siren, property_serializer=property_serializer)

    def entity(
        self,
        resource_name: str,
        properties: Any,
        *,
        operations: tuple[str, ...],
        path_values: Mapping[str, Any] = EMPTY_VALUES,
        entities: tuple[SirenEmbeddedEntity, ...] = (),
        related_links: tuple[RelatedLinkInput, ...] = (),
        status_code: int = 200,
        headers: Mapping[str, str] = EMPTY_HEADERS,
    ) -> NinjaExtraSirenResponse:
        if status_code == 204:
            raise ValueError("Siren entity responses cannot use 204 No Content; call no_content()")
        serialized = self._properties.serialize(properties)
        document = self._siren.document(
            SirenEntityRequest(
                resource_name=resource_name,
                properties=dict(serialized),
                operation_ids=operations,
                path_values=dict(path_values),
                entities=entities,
                related_links=related_links,
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
        serialized = SirenCollectionRequest(
            resource_name=request.resource_name,
            items=serialize_collection_items(self._properties, request.items),
            collection_operation_ids=request.collection_operation_ids,
            item_operation_ids=request.item_operation_ids,
            path_values=request.path_values,
            pagination=request.pagination,
        )
        return self._responses.create(
            self._siren.collection(serialized),
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
