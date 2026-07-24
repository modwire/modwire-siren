from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from ...graph import SirenApi, SirenOperation, SirenResource
from ...request import SirenContext


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
