from collections.abc import Mapping
from typing import Any

from ..contracts.action import SirenAction
from ..openapi.catalog import SirenResourceCatalog
from ..openapi.href import SirenHrefResolver
from ..standards import SirenMediaType
from .field import SirenFieldFactory


class SirenActionFactory:
    def __init__(
        self,
        catalog: SirenResourceCatalog,
        hrefs: SirenHrefResolver,
        fields: SirenFieldFactory,
    ):
        self._catalog = catalog
        self._hrefs = hrefs
        self._fields = fields

    def create(self, operation_id: str, path_values: Mapping[str, Any]) -> SirenAction:
        operation = self._catalog.operation(operation_id)
        return SirenAction(
            **operation.model_dump(include={"method", "title"}),
            name=operation.operation_id,
            href=self._hrefs.resolve(operation.path, path_values),
            media_type=SirenMediaType.ACTION,
            fields=tuple(self._fields.create(field) for field in operation.fields),
        )
