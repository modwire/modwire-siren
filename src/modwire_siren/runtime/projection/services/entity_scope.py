from dataclasses import dataclass

from wireup import injectable

from ...document import SirenDocument
from ..contracts import SirenEntityDocumentService, SirenScopeProjector
from ..values import SirenProjectionRequest


@injectable(as_type=SirenScopeProjector, qualifier="entity")
@dataclass(frozen=True)
class SirenEntityScopeProjector(SirenScopeProjector):
    entities: SirenEntityDocumentService

    def supports(self, scope: str) -> bool:
        return scope == "entity"

    def project(self, request: SirenProjectionRequest) -> SirenDocument:
        if request.resource is None:
            raise ValueError("Siren entity projection requires a resource")
        document = self.entities.entity(request.api, request.resource, request.value, request.context, request.rel)
        if isinstance(document, SirenDocument):
            return document
        raise ValueError("Siren entity projection produced an embedded representation")
