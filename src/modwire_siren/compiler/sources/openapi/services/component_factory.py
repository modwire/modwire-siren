from dataclasses import dataclass
from typing import Any

from wireup import injectable

from ..contracts import OpenApiComponentResolverFactory
from ..state import ComponentResolver


@injectable(as_type=OpenApiComponentResolverFactory)
@dataclass(frozen=True)
class OpenApiDefaultComponentResolverFactory(OpenApiComponentResolverFactory):
    def create(self, components: Any) -> ComponentResolver:
        return ComponentResolver(components)
