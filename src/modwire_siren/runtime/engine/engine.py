from dataclasses import dataclass

from ..document import SirenDocument
from ..errors import SirenProjectionError
from ..graph import SirenApi
from ..projection import SirenProjectionService
from ..request import SirenContext


@dataclass(frozen=True)
class SirenEngine:
    api: SirenApi
    projection: SirenProjectionService

    def project(self, context: SirenContext) -> SirenDocument:
        try:
            return self.projection.project(self.api, context)
        except Exception as error:
            raise SirenProjectionError("Siren projection failed") from error
