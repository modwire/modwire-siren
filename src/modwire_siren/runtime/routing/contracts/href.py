from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from ...graph import SirenResource
from ...request import SirenContext
from ...vocabulary import SirenUri


class SirenHrefService(ABC):
    @abstractmethod
    def href(
        self,
        path: str,
        context: SirenContext,
        resource: SirenResource | None,
        value: Mapping[str, Any] | None = None,
        include_query: bool = True,
    ) -> SirenUri:
        pass
