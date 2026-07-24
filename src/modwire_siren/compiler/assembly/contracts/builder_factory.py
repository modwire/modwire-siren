from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..state.builder import SirenBuilder


class SirenBuilderFactory(ABC):
    @abstractmethod
    def create(self) -> "SirenBuilder":
        raise NotImplementedError
