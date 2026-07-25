from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from ....vocabulary import SirenRelation
from ...document import SirenDocument, SirenEmbeddedRepresentation
from ...graph import SirenApi, SirenResource
from ...request import SirenContext


class SirenEntityDocumentService(ABC):
    @abstractmethod
    def entity(
        self,
        api: SirenApi,
        resource: SirenResource,
        value: Mapping[str, Any],
        context: SirenContext,
        rel: tuple[SirenRelation, ...],
    ) -> SirenDocument | SirenEmbeddedRepresentation:
        raise NotImplementedError
