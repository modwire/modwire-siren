from abc import ABC, abstractmethod
from typing import Any

from modwire_siren.shared import ModwireSirenError

from ....runtime.graph import SirenApi
from ...compatibility import SirenCompatibilityFinding


class SirenSource(ABC):
    @abstractmethod
    def load(self, schema: dict[str, Any], root_path: str) -> SirenApi:
        raise ModwireSirenError

    @abstractmethod
    def audit(self, schema: dict[str, Any]) -> tuple[SirenCompatibilityFinding, ...]:
        raise ModwireSirenError
