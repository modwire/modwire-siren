from dataclasses import dataclass
from typing import Any

from wireup import injectable

from ...routing import SirenHrefService
from ..contracts import SirenActionDocumentService, SirenEntityDocumentService, SirenScopeProjector
from ..values import SirenProjectionRequest


@injectable(as_type=SirenScopeProjector, qualifier="collection")
@dataclass(frozen=True)
class SirenCollectionScopeProjector(SirenScopeProjector):
    actions: SirenActionDocumentService
    entities: SirenEntityDocumentService
    hrefs: SirenHrefService

    def supports(self, scope: str) -> bool:
        return scope == "collection"

    def project(self, request: SirenProjectionRequest) -> dict[str, Any]:
        if request.resource is None:
            raise ValueError("Siren collection projection requires a resource")
        return {
            "class": ["collection", request.resource.resource_class],
            "properties": dict(request.context.value),
            "entities": [
                self.entities.entity(request.api, request.resource, item, request.context, ("item",))
                for item in request.context.items
            ],
            "actions": self.actions.actions(
                request.api, request.resource, "collection", request.context, request.context.value
            ),
            "links": [
                {
                    "rel": ["self"],
                    "href": self.hrefs.href(request.resource.collection.path, request.context, request.resource),
                }
            ],
        }
