from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from wireup import injectable

from ....runtime import SirenApi
from ...sources import SirenSource
from ..contracts import SirenApiAssembler


@injectable
@dataclass(frozen=True)
class SirenApiService:
    """Build a validated Siren API graph from one or more sources."""

    sources: Sequence[SirenSource]
    assembler: SirenApiAssembler

    def build(self, schema: dict[str, Any], root_path: str = "/") -> SirenApi:
        return self.assembler.assemble(tuple(source.load(schema, root_path) for source in self.sources))
