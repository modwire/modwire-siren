from abc import ABC, abstractmethod
from typing import Any

from ....runtime.graph import SirenApi
from ...compatibility import SirenCompatibilityFinding


class SirenSource(ABC):
    @abstractmethod
    def load(self, schema: dict[str, Any], root_path: str) -> SirenApi:
        raise NotImplementedError

    @abstractmethod
    def audit(self, schema: dict[str, Any]) -> tuple[SirenCompatibilityFinding, ...]:
        raise NotImplementedError
