from dataclasses import dataclass

from wireup import injectable

from modwire_siren.contexts.graph import SirenApi

from ...projection import SirenProjectionService
from ..state import SirenEngine


@injectable
@dataclass(frozen=True)
class SirenEngineFactory:
    projection: SirenProjectionService

    def create(self, api: SirenApi) -> SirenEngine:
        return SirenEngine(api=api, projection=self.projection)
