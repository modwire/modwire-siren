from typing import Any

from .contracts.entity import SirenEntityRequest
from .factories.entity import SirenEntityFactory
from .serialization import SirenSerializer


class ModwireSiren:
    """Project validated entity requests into serialized Siren documents."""

    def __init__(self, entities: SirenEntityFactory, serializer: SirenSerializer):
        self._entities = entities
        self._serializer = serializer

    def document(self, request: SirenEntityRequest) -> dict[str, Any]:
        """Build and serialize one Siren entity document."""
        return self._serializer.serialize(self._entities.create(request))
