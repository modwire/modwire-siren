from collections.abc import Mapping
from typing import Any

from .engine import SirenEngine
from .service import SirenApiService
from .sources import OpenApiSource


def siren(openapi: Mapping[str, Any], *, root_path: str = "/") -> SirenEngine:
    """Compile an OpenAPI document into a reusable Siren engine."""
    if not isinstance(openapi, Mapping):
        raise TypeError("OpenAPI document must be a mapping")
    if not isinstance(root_path, str) or not root_path.startswith("/"):
        raise ValueError("Siren root path must start with '/'")
    api = SirenApiService((OpenApiSource(root_path=root_path),)).build(dict(openapi))
    return SirenEngine(api)
