from dataclasses import dataclass

from modwire_siren.shared import ModwireSirenError

from ...document import SirenDocument
from ...graph import SirenApi
from ...projection import SirenProjectionService
from ...request import SirenContext


@dataclass(frozen=True)
class SirenEngine:
    api: SirenApi
    projection: SirenProjectionService

    def project(self, context: SirenContext) -> SirenDocument:
        try:
            return self.projection.project(self.api, context)
        except Exception as error:
            raise ModwireSirenError("Siren projection failed") from error
