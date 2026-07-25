from modwire_siren.contexts.shared import BaseState, ModwireSirenError

from ...document import SirenDocument
from ...graph import SirenApi
from ...projection import SirenProjectionService
from ...request import SirenContext


class SirenEngine(BaseState):
    api: SirenApi
    projection: SirenProjectionService

    def project(self, context: SirenContext) -> SirenDocument:
        try:
            return self.projection.project(self.api, context)
        except Exception as error:
            raise ModwireSirenError("Siren projection failed") from error
