from dataclasses import dataclass

from wireup import injectable

from ......runtime.document import SirenFieldValue
from ....contracts import SirenContractSource
from ....values import SirenCapability
from ..exporter import SirenSerializationSchemaExporter


@injectable(as_type=SirenContractSource, qualifier=SirenFieldValue)
@dataclass(frozen=True)
class SirenFieldValueContractSource(SirenContractSource):
    exporter: SirenSerializationSchemaExporter

    def capability(self) -> SirenCapability:
        return self.exporter.export("FieldValueObject", SirenFieldValue)
