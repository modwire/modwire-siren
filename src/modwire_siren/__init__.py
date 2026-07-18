from ._version import __version__
from .client.contracts import SirenResponse, SirenTransport
from .client.error import SirenClientError
from .client.facade import SirenClient
from .composition import ModwireSirenFactory
from .contracts.collection import CustomPagination, OffsetPagination, PaginationLinkInput, SirenCollectionRequest
from .contracts.entity import SirenEntityRequest
from .facade import ModwireSiren
from .integrations.ninja_extra import (
    NinjaExtraSirenController,
    NinjaExtraSirenResponse,
    NinjaExtraSirenResponseAdapter,
    SirenEntityDecorator,
    siren_entity,
)
from .openapi.error import OpenApiError

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
    "SirenClient",
    "SirenClientError",
    "SirenCollectionRequest",
    "SirenEntityDecorator",
    "SirenEntityRequest",
    "SirenResponse",
    "SirenTransport",
    "__version__",
    "siren_entity",
]
