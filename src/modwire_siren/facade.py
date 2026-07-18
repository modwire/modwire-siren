from typing import Any

from .contracts.collection import SirenCollectionRequest
from .contracts.entity import SirenEntityRequest
from .factories.collection import SirenCollectionFactory
from .factories.entity import SirenEntityFactory
from .serialization import SirenSerializer


class ModwireSiren:
    """Project validated entity requests into serialized Siren documents."""

    def __init__(self, entities: SirenEntityFactory, collections: SirenCollectionFactory, serializer: SirenSerializer):
        self._entities = entities
        self._collections = collections
        self._serializer = serializer

    def document(self, request: SirenEntityRequest) -> dict[str, Any]:
        """Build and serialize one Siren entity document."""
        return self._serializer.serialize(self._entities.create(request))

    def collection(self, request: SirenCollectionRequest) -> dict[str, Any]:
        """Build and serialize one Siren collection document."""
        return self._serializer.serialize(self._collections.create(request))
