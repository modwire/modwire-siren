from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..services.components import ComponentResolver


class OpenApiComponentResolverFactory(ABC):
    @abstractmethod
    def create(self, components: Any) -> "ComponentResolver":
        raise NotImplementedError
