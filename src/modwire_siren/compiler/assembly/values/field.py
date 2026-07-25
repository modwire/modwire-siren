from dataclasses import dataclass

from ....vocabulary import SirenFieldType


@dataclass(frozen=True)
class FieldDraft:
    operation: str
    name: str
    type: SirenFieldType
