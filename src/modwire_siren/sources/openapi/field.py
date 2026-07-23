from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Field:
    name: str
    definition: dict[str, Any]
    required: bool
