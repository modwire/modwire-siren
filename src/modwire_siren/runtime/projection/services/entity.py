from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from wireup import injectable

from ...graph import SirenApi, SirenResource
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
        rel: tuple[str, ...],
    ) -> dict[str, Any]:
        document: dict[str, Any] = {
            "class": [resource.resource_class],
            "properties": dict(value),
            "actions": self.actions.actions(api, resource, "entity", context, value),
            "links": [
                {
                    "rel": ["self"],
                    "href": self.hrefs.href(
                        resource.entity.path if resource.entity else resource.collection.path, context, resource, value
                    ),
                }
            ],
        }
        if rel:
            document["rel"] = list(rel)
        return document
