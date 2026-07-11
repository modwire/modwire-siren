from ._version import __version__
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
    "SirenEntityDecorator",
    "SirenEntityRequest",
    "__version__",
]
