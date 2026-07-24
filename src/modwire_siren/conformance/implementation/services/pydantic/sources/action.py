from dataclasses import dataclass

from wireup import injectable

from ......runtime.document import SirenAction
from ....contracts import SirenContractSource
from ....values import SirenCapability
from ..exporter import SirenSerializationSchemaExporter


@injectable(as_type=SirenContractSource, qualifier=SirenAction)
@dataclass(frozen=True)
class SirenActionContractSource(SirenContractSource):
    exporter: SirenSerializationSchemaExporter

    def capability(self) -> SirenCapability:
        return self.exporter.export("Action", SirenAction)
