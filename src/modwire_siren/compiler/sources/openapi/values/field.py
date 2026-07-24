from dataclasses import dataclass


@dataclass(frozen=True)
class Field:
    name: str
    type: str
