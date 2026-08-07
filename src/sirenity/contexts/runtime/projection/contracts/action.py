from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from sirenity.contexts.graph import SirenApi, SirenOperation, SirenResource
from sirenity.contexts.shared import ModwireSirenError, SirenScope

from ...document import SirenAction
from ...request import SirenContext


class SirenActionDocumentService(ABC):
    @abstractmethod
    def actions(
        self,
        api: SirenApi,
        resource: SirenResource,
        scope: SirenScope,
        context: SirenContext,
        value: Mapping[str, Any],
    ) -> list[SirenAction]:
        raise ModwireSirenError

    @abstractmethod
    def action(
        self,
        operation: SirenOperation,
        context: SirenContext,
        resource: SirenResource | None,
        value: Mapping[str, Any],
        include_query: bool = True,
    ) -> SirenAction:
        raise ModwireSirenError
