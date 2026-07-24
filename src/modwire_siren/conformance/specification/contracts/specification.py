from abc import ABC, abstractmethod

from ..values import SirenRequirement


class SirenSpecification(ABC):
    @abstractmethod
    def requirements(self) -> tuple[SirenRequirement, ...]:
        raise NotImplementedError
