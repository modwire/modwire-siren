from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from wireup import injectable

from modwire_siren.contexts.graph import SirenApi, SirenResource
from modwire_siren.contexts.shared import SirenRelation, SirenScope

from ...document import SirenDocument, SirenEmbeddedRepresentation, SirenLink
from ...request import SirenContext
from ...routing import SirenHrefService
from ..contracts import SirenActionDocumentService, SirenEntityDocumentService


@injectable(as_type=SirenEntityDocumentService)
@dataclass(frozen=True)
class SirenDefaultEntityDocumentService(SirenEntityDocumentService):
    actions: SirenActionDocumentService
    hrefs: SirenHrefService

    def entity(
        self,
        api: SirenApi,
        resource: SirenResource,
        value: Mapping[str, Any],
        context: SirenContext,
        rel: tuple[SirenRelation, ...],
    ) -> SirenDocument | SirenEmbeddedRepresentation:
        title = context.title or resource.title
        fields = {
            "class_": (resource.resource_class,),
            "title": title,
            "properties": value,
            "actions": tuple(self.actions.actions(api, resource, SirenScope.ENTITY, context, value)) or None,
            "links": (
                SirenLink(
                    rel=("self",),
                    title=title,
                    href=self.hrefs.href(
                        resource.entity.path if resource.entity else resource.collection.path, context, resource, value
                    ),
                ),
            ),
        }
        if rel:
            return SirenEmbeddedRepresentation(rel=rel, **fields)
        return SirenDocument(**fields)
