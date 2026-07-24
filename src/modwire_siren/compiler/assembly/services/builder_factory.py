from dataclasses import dataclass

from wireup import injectable

from ..contracts import SirenBuilderFactory
from .builder import SirenBuilder


@injectable(as_type=SirenBuilderFactory)
@dataclass(frozen=True)
class SirenDefaultBuilderFactory(SirenBuilderFactory):
    def create(self) -> SirenBuilder:
        return SirenBuilder()
