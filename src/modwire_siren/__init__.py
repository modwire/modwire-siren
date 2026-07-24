from .api import Siren
from .runtime import SirenContext

siren = Siren()

__all__ = [
    "SirenContext",
    "siren",
]
