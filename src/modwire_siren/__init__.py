from ._version import __version__
from .client.contracts import SirenResponse, SirenTransport
from .client.error import SirenClientError
from .client.facade import SirenClient
from .composition import ModwireSirenFactory
from .contracts.collection import CustomPagination, OffsetPagination, PaginationLinkInput, SirenCollectionRequest
from .contracts.entity import SirenEntityRequest
from .contracts.related_link import RelatedLinkInput
from .facade import ModwireSiren
from .integrations.ninja_extra import (
    NinjaExtraSirenController,
    NinjaExtraSirenResponse,
    NinjaExtraSirenResponseAdapter,
    SirenEntityDecorator,
    collect_siren_resources,
    siren_collection,
    siren_entity,
    siren_resource,
)
from .openapi.error import OpenApiError
from .openapi.relation_spec import SirenRelationSpec
from .openapi.resource_api import inject_siren_resources, validate_siren_resources
from .openapi.resource_spec import SirenResourceSpec

__all__ = [
    "CustomPagination",
    "ModwireSiren",
    "ModwireSirenFactory",
    "NinjaExtraSirenController",
    "NinjaExtraSirenResponse",
    "NinjaExtraSirenResponseAdapter",
    "OffsetPagination",
    "OpenApiError",
    "PaginationLinkInput",
    "RelatedLinkInput",
    "SirenClient",
    "SirenClientError",
    "SirenCollectionRequest",
    "SirenEntityDecorator",
    "SirenEntityRequest",
    "SirenRelationSpec",
    "SirenResourceSpec",
    "SirenResponse",
    "SirenTransport",
    "__version__",
    "collect_siren_resources",
    "inject_siren_resources",
    "siren_collection",
    "siren_entity",
    "siren_resource",
    "validate_siren_resources",
]
