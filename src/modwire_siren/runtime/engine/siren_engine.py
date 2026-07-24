from typing import Any

from ..projection import SirenProjectionService
from ..siren_api import SirenApi
from ..siren_context import SirenContext


class SirenEngine:
    def __init__(self, api: SirenApi, projection: SirenProjectionService):
        self._api = api
        self._projection = projection

    def project(self, context: SirenContext) -> dict[str, Any]:
        return self._projection.project(self._api, context)
