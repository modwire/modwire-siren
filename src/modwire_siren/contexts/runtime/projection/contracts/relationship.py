from abc import ABC, abstractmethod

from modwire_siren.contexts.graph import SirenApi

from ...document import SirenEmbeddedRepresentation, SirenLink
from ...request import SirenContext


class SirenRelationshipDocumentService(ABC):
    @abstractmethod
    def relationships(
        self, api: SirenApi, context: SirenContext
    ) -> tuple[SirenLink | SirenEmbeddedRepresentation, ...]:
        raise NotImplementedError
