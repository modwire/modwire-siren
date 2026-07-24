from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....assembly.state.builder import SirenBuilder
    from ..state.components import ComponentResolver
    from ..state.routes import RouteCatalog


class OpenApiOperationCompiler(ABC):
    @abstractmethod
    def compile(self, builder: "SirenBuilder", routes: "RouteCatalog", components: "ComponentResolver") -> None:
        raise NotImplementedError
