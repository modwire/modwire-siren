from dataclasses import dataclass

from modwire_siren.shared import SirenFieldType


@dataclass(frozen=True)
class FieldDraft:
    operation: str
    name: str
    type: SirenFieldType
