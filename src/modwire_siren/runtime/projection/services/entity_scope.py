from dataclasses import dataclass
from typing import Any

from wireup import injectable

from ..contracts import SirenEntityDocumentService, SirenScopeProjector
from ..values import SirenProjectionRequest


@injectable(as_type=SirenScopeProjector, qualifier="entity")
@dataclass(frozen=True)
class SirenEntityScopeProjector(SirenScopeProjector):
    entities: SirenEntityDocumentService

    def supports(self, scope: str) -> bool:
        return scope == "entity"

    def project(self, request: SirenProjectionRequest) -> dict[str, Any]:
        if request.resource is None:
            raise ValueError("Siren entity projection requires a resource")
        return self.entities.entity(request.api, request.resource, request.value, request.context, request.rel)
