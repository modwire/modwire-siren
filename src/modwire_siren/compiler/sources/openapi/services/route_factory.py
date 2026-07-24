from dataclasses import dataclass
from typing import Any

from wireup import injectable

from ..contracts import OpenApiRouteCatalogFactory
from ..state import RouteCatalog


@injectable(as_type=OpenApiRouteCatalogFactory)
@dataclass(frozen=True)
class OpenApiDefaultRouteCatalogFactory(OpenApiRouteCatalogFactory):
    def create(self, paths: dict[str, Any]) -> RouteCatalog:
        return RouteCatalog(paths)
