from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from wireup import injectable

from ...routing import SirenHrefService
from ...siren_api import SirenApi
from ...siren_context import SirenContext
from ...siren_operation import SirenOperation
from ...siren_resource import SirenResource
from ..contracts import SirenActionDocumentService


@injectable(as_type=SirenActionDocumentService)
@dataclass(frozen=True)
class SirenDefaultActionDocumentService(SirenActionDocumentService):
    hrefs: SirenHrefService

    def actions(
        self,
        api: SirenApi,
        resource: SirenResource,
        scope: str,
        context: SirenContext,
        value: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        names = resource.collection_operations if scope == "collection" else resource.entity_operations
        operations = {operation.name: operation for operation in api.operations}
        return [
            self.action(operations[name], context, resource, value)
            for name in names
            if name in context.capabilities
        ]

    def action(
        self,
        operation: SirenOperation,
        context: SirenContext,
        resource: SirenResource | None,
        value: Mapping[str, Any],
        include_query: bool = True,
    ) -> dict[str, Any]:
        action: dict[str, Any] = {
            "name": operation.name,
            "href": self.hrefs.href(operation.route.path, context, resource, value, include_query),
            "method": operation.method,
        }
        if operation.media_type is not None:
            action["type"] = operation.media_type
        if operation.fields:
            action["fields"] = [
                {"name": field.name, "type": field.definition.get("type", "text"), "required": field.required}
                for field in operation.fields
            ]
        return action
