from dataclasses import dataclass

from wireup import injectable

from ......runtime.document import SirenLink
from ....contracts import SirenContractSource
from ....values import SirenCapability
from ..exporter import SirenSerializationSchemaExporter


@injectable(as_type=SirenContractSource, qualifier=SirenLink)
@dataclass(frozen=True)
class SirenLinkContractSource(SirenContractSource):
    exporter: SirenSerializationSchemaExporter

    def capability(self) -> SirenCapability:
        return self.exporter.export("Link", SirenLink)
