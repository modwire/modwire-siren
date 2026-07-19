from abc import ABC, abstractmethod
from typing import Any

from ..contracts import SirenApi


class SirenSource(ABC):
    @abstractmethod
    def load(self, schema: dict[str, Any]) -> SirenApi:
        raise NotImplementedError
