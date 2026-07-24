from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from ...siren_context import SirenContext
from ...siren_resource import SirenResource


class SirenHrefService(ABC):
    @abstractmethod
    def href(
        self,
        path: str,
        context: SirenContext,
        resource: SirenResource | None,
        value: Mapping[str, Any] | None = None,
        include_query: bool = True,
    ) -> str:
        pass
