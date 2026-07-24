from dataclasses import dataclass

from wireup import injectable

from ......runtime.document import SirenEmbeddedRepresentation
from ....contracts import SirenContractSource
from ....values import SirenCapability
from ..exporter import SirenSerializationSchemaExporter


@injectable(as_type=SirenContractSource, qualifier=SirenEmbeddedRepresentation)
@dataclass(frozen=True)
class SirenEmbeddedRepresentationContractSource(SirenContractSource):
    exporter: SirenSerializationSchemaExporter

    def capability(self) -> SirenCapability:
        return self.exporter.export(
            "EmbeddedRepresentationSubEntity", SirenEmbeddedRepresentation
        )
