from dataclasses import dataclass

from wireup import injectable

from ......runtime.document import SirenEmbeddedLink
from ....contracts import SirenContractSource
from ....values import SirenCapability
from ..exporter import SirenSerializationSchemaExporter


@injectable(as_type=SirenContractSource, qualifier=SirenEmbeddedLink)
@dataclass(frozen=True)
class SirenEmbeddedLinkContractSource(SirenContractSource):
    exporter: SirenSerializationSchemaExporter

    def capability(self) -> SirenCapability:
        return self.exporter.export("EmbeddedLinkSubEntity", SirenEmbeddedLink)
