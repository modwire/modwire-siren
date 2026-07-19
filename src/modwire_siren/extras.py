from typing import Any

from .engine import SirenEngine
from .service import SirenApiService
from .sources import OpenApiSource


def siren(openapi: dict[str, Any]) -> SirenEngine:
    api = SirenApiService((OpenApiSource(),)).build(openapi)
    return SirenEngine(api)
