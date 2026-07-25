from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from ...document import SirenAction
from ...graph import SirenApi, SirenOperation, SirenResource
from ...request import SirenContext
from ...vocabulary import SirenScope


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
        raise NotImplementedError

    @abstractmethod
    def action(
        self,
        operation: SirenOperation,
        context: SirenContext,
        resource: SirenResource | None,
        value: Mapping[str, Any],
        include_query: bool = True,
    ) -> SirenAction:
        raise NotImplementedError
