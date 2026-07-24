from abc import ABC, abstractmethod

from ..values import SirenBuilder


class SirenBuilderFactory(ABC):
    @abstractmethod
    def create(self) -> SirenBuilder:
        raise NotImplementedError
