from dataclasses import dataclass

from wireup import injectable

from modwire_siren.contexts.runtime.document import SirenDocument

from ..contracts import SirenContractSource
from ..values import SirenCapability
from .exporter import SirenSerializationSchemaExporter


@injectable(as_type=SirenContractSource, qualifier=SirenDocument)
@dataclass(frozen=True)
class SirenDocumentContractSource(SirenContractSource):
    exporter: SirenSerializationSchemaExporter

    def capability(self) -> SirenCapability:
        return self.exporter.export("Entity", SirenDocument)
