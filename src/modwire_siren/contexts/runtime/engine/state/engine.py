from modwire_siren.contexts.graph import SirenApi
from modwire_siren.contexts.shared import BaseState, ModwireSirenError

from ...document import SirenDocument
from ...projection import SirenProjectionService, SirenResponseProjectionService
from ...request import SirenContext, SirenResponseContext


class SirenEngine(BaseState):
    api: SirenApi
    projection: SirenProjectionService
    response_projection: SirenResponseProjectionService

    def project(self, context: SirenContext) -> SirenDocument:
        try:
            return self.projection.project(self.api, context)
        except Exception as error:
            raise ModwireSirenError("Siren projection failed") from error

    def project_response(self, context: SirenResponseContext) -> SirenDocument:
        try:
            return self.response_projection.project(self.api, context)
        except Exception as error:
            raise ModwireSirenError("Siren response projection failed") from error
