from dataclasses import dataclass

from wireup import injectable

from modwire_siren.contexts.graph import SirenApi

from ...operation_input import SirenOperationInputService
from ...projection import SirenProjectionService, SirenResponseProjectionService
from ..state import SirenEngine


@injectable
@dataclass(frozen=True)
class SirenEngineFactory:
    projection: SirenProjectionService
    response_projection: SirenResponseProjectionService
    operation_inputs: SirenOperationInputService

    def create(self, api: SirenApi) -> SirenEngine:
        return SirenEngine(
            api=api,
            projection=self.projection,
            response_projection=self.response_projection,
            operation_inputs=self.operation_inputs,
        )
