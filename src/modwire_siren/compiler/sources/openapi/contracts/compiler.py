from abc import ABC, abstractmethod

from ....assembly.values import SirenBuilder
from ..values import ComponentResolver, RouteCatalog


class OpenApiOperationCompiler(ABC):
    @abstractmethod
    def compile(self, builder: SirenBuilder, routes: RouteCatalog, components: ComponentResolver) -> None:
        raise NotImplementedError
