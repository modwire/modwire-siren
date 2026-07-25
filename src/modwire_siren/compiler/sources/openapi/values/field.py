from dataclasses import dataclass

from modwire_siren.shared import SirenFieldType


@dataclass(frozen=True)
class Field:
    name: str
    type: SirenFieldType
