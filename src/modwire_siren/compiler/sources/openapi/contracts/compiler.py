from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....assembly.services.builder import SirenBuilder
    from ..services.components import ComponentResolver
    from ..services.routes import RouteCatalog


class OpenApiOperationCompiler(ABC):
    @abstractmethod
    def compile(self, builder: "SirenBuilder", routes: "RouteCatalog", components: "ComponentResolver") -> None:
        raise NotImplementedError
