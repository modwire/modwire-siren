from dataclasses import dataclass

from wireup import injectable

from ...document import SirenDocument, SirenLink
from ...routing import SirenHrefService
from ...vocabulary import SirenScope
from ..contracts import SirenActionDocumentService, SirenEntityDocumentService, SirenScopeProjector
from ..values import SirenProjectionRequest


@injectable(as_type=SirenScopeProjector, qualifier=SirenScope.COLLECTION)
@dataclass(frozen=True)
class SirenCollectionScopeProjector(SirenScopeProjector):
    actions: SirenActionDocumentService
    entities: SirenEntityDocumentService
    hrefs: SirenHrefService

    def supports(self, scope: SirenScope) -> bool:
        return scope == SirenScope.COLLECTION

    def project(self, request: SirenProjectionRequest) -> SirenDocument:
        if request.resource is None:
            raise ValueError("Siren collection projection requires a resource")
        return SirenDocument(
            class_=(SirenScope.COLLECTION, request.resource.resource_class),
            properties=request.context.value,
            entities=tuple(
                self.entities.entity(request.api, request.resource, item, request.context, ("item",))
                for item in request.context.items
            ) or None,
            actions=tuple(self.actions.actions(
                request.api, request.resource, SirenScope.COLLECTION, request.context, request.context.value
            )) or None,
            links=(
                SirenLink(
                    rel=("self",),
                    href=self.hrefs.href(request.resource.collection.path, request.context, request.resource),
                ),
            ),
        )
