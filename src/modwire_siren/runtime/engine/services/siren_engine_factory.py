from dataclasses import dataclass

from wireup import injectable

from ...graph import SirenApi
from ...projection import SirenProjectionService
from ..siren_engine import SirenEngine


@injectable
@dataclass(frozen=True)
class SirenEngineFactory:
    projection: SirenProjectionService

    def create(self, api: SirenApi) -> SirenEngine:
        return SirenEngine(api, self.projection)
