from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from ...siren_api import SirenApi
from ...siren_context import SirenContext
from ...siren_operation import SirenOperation
from ...siren_resource import SirenResource


class SirenActionDocumentService(ABC):
    @abstractmethod
    def actions(
        self,
        api: SirenApi,
        resource: SirenResource,
        scope: str,
        context: SirenContext,
        value: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def action(
        self,
        operation: SirenOperation,
        context: SirenContext,
        resource: SirenResource | None,
        value: Mapping[str, Any],
        include_query: bool = True,
    ) -> dict[str, Any]:
        pass
