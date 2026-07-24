from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from ...siren_api import SirenApi
from ...siren_context import SirenContext
from ...siren_resource import SirenResource


class SirenEntityDocumentService(ABC):
    @abstractmethod
    def entity(
        self,
        api: SirenApi,
        resource: SirenResource,
        value: Mapping[str, Any],
        context: SirenContext,
        rel: tuple[str, ...],
    ) -> dict[str, Any]:
        pass
