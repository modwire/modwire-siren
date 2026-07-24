from dataclasses import dataclass
from typing import Any

from ..graph import SirenApi
from ..projection import SirenProjectionService
from ..request import SirenContext


@dataclass(frozen=True)
class SirenEngine:
    api: SirenApi
    projection: SirenProjectionService

    def project(self, context: SirenContext) -> dict[str, Any]:
        return self.projection.project(self.api, context)
