from dataclasses import dataclass

from wireup import injectable

from modwire_siren.contexts.runtime.document import SirenField

from ..contracts import SirenContractSource
from ..values import SirenCapability
from .exporter import SirenSerializationSchemaExporter


@injectable(as_type=SirenContractSource, qualifier=SirenField)
@dataclass(frozen=True)
class SirenFieldContractSource(SirenContractSource):
    exporter: SirenSerializationSchemaExporter

    def capability(self) -> SirenCapability:
        return self.exporter.export("Field", SirenField)
