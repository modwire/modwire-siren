from dataclasses import dataclass

from .....vocabulary import SirenFieldType


@dataclass(frozen=True)
class Field:
    name: str
    type: SirenFieldType
