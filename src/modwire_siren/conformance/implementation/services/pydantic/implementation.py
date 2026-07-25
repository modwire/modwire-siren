from collections.abc import Sequence
from dataclasses import dataclass

from wireup import injectable

from ...contracts import SirenContractSource, SirenImplementation
from ...values import SirenCapability


@injectable(as_type=SirenImplementation)
@dataclass(frozen=True)
class PydanticSirenImplementation(SirenImplementation):
    sources: Sequence[SirenContractSource]

    def capabilities(self) -> tuple[SirenCapability, ...]:
        capabilities = tuple(source.capability() for source in self.sources)
        definitions = {capability.definition for capability in capabilities}
        if len(definitions) != len(capabilities):
            message = "Siren contract sources must provide unique official definitions."
            raise ValueError(message)
        return capabilities
