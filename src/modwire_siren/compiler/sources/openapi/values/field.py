from dataclasses import dataclass

from .....runtime.vocabulary import SirenFieldType


@dataclass(frozen=True)
class Field:
    name: str
    type: SirenFieldType
