from ._version import __version__
from .client.contracts import SirenResponse, SirenTransport
from .client.error import SirenClientError
from .client.facade import SirenClient
from .composition import ModwireSirenFactory
from .contracts.entity import SirenEntityRequest
from .facade import ModwireSiren
from .integrations.ninja_extra import NinjaExtraSirenController, SirenEntityDecorator
from .openapi.error import OpenApiError

__all__ = [
    "ModwireSiren",
    "ModwireSirenFactory",
    "NinjaExtraSirenController",
    "OpenApiError",
    "SirenClient",
    "SirenClientError",
    "SirenEntityDecorator",
    "SirenEntityRequest",
    "SirenResponse",
    "SirenTransport",
    "__version__",
]
