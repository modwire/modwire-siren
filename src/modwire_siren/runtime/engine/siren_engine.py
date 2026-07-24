from typing import Any

from ..graph import SirenApi
from ..projection import SirenProjectionService
from ..request import SirenContext


class SirenEngine:
    def __init__(self, api: SirenApi, projection: SirenProjectionService):
        self._api = api
        self._projection = projection

    def project(self, context: SirenContext) -> dict[str, Any]:
        return self._projection.project(self._api, context)
