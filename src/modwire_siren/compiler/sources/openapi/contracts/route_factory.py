from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..services.routes import RouteCatalog


class OpenApiRouteCatalogFactory(ABC):
    @abstractmethod
    def create(self, paths: dict[str, Any]) -> "RouteCatalog":
        raise NotImplementedError
