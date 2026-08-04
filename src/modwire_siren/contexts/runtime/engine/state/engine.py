from modwire_siren.contexts.graph import SirenApi
from modwire_siren.contexts.shared import BaseState, ModwireSirenError

from ...document import SirenDocument
from ...operation_input import SirenOperationInput, SirenOperationInputService
from ...projection import SirenProjectionService, SirenResponseProjectionService
from ...request import SirenContext, SirenResponseContext


class SirenEngine(BaseState):
    api: SirenApi
    projection: SirenProjectionService
    response_projection: SirenResponseProjectionService
    operation_inputs: SirenOperationInputService

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

    def operation_input(self, operation_id: str) -> SirenOperationInput | None:
        try:
            return self.operation_inputs.input(self.api, operation_id)
        except Exception as error:
            raise ModwireSirenError("Siren operation input lookup failed") from error
