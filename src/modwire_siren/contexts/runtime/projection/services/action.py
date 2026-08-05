from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from wireup import injectable

from modwire_siren.contexts.graph import SirenApi, SirenOperation, SirenResource
from modwire_siren.contexts.shared import SirenScope

from ...document import SirenAction, SirenField, SirenFieldValue
from ...request import SirenContext
from ...routing import SirenHrefService
from ..contracts import SirenActionDocumentService


@injectable(as_type=SirenActionDocumentService)
@dataclass(frozen=True)
class SirenDefaultActionDocumentService(SirenActionDocumentService):
    hrefs: SirenHrefService

    def actions(
        self,
        api: SirenApi,
        resource: SirenResource,
        scope: SirenScope,
        context: SirenContext,
        value: Mapping[str, Any],
    ) -> list[SirenAction]:
        names = resource.collection_operations if scope == SirenScope.COLLECTION else resource.entity_operations
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
    ) -> SirenAction:
        return SirenAction(
            name=operation.name,
            href=self.hrefs.href(operation.route.path, context, resource, value, include_query),
            method=operation.method,
            title=operation.title,
            type=operation.media_type,
            fields=tuple(
                SirenField(
                    name=field.name,
                    type=field.type,
                    title=field.title,
                    value=(
                        tuple(SirenFieldValue(value=value, selected=value == field.default) for value in field.values)
                        if field.values else field.default
                    ),
                )
                for field in operation.fields
            ) or None,
        )
