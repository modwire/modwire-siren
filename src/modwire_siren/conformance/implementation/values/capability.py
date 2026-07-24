from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SirenCapability:
    definition: str
    schema: Mapping[str, Any]
