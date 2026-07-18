from collections.abc import Mapping
from typing import Any

from .contracts.collection import SirenCollectionRequest
from .contracts.entity import SirenEntityRequest
from .contracts.root import SirenRootRequest
from .factories.collection import SirenCollectionFactory
from .factories.entity import SirenEntityFactory
from .factories.root import SirenRootFactory
from .serialization import SirenSerializer


class ModwireSiren:
    """Project validated entity requests into serialized Siren documents."""

    def __init__(
        self,
        entities: SirenEntityFactory,
        collections: SirenCollectionFactory,
        roots: SirenRootFactory,
        serializer: SirenSerializer,
    ):
        self._entities = entities
        self._collections = collections
        self._roots = roots
        self._serializer = serializer

    def document(self, request: SirenEntityRequest) -> dict[str, Any]:
        """Build and serialize one Siren entity document."""
        return self._serializer.serialize(self._entities.create(request))

    def collection(self, request: SirenCollectionRequest) -> dict[str, Any]:
        """Build and serialize one Siren collection document."""
        return self._serializer.serialize(self._collections.create(request))

    def root(
        self,
        *,
        self_href: str,
        title: str = "",
        version: str = "",
        service_desc_href: str = "",
        extra_links: tuple[Mapping[str, Any], ...] = (),
    ) -> dict[str, Any]:
        """Build one Siren API entry-point document."""
        return self._roots.create(
            SirenRootRequest(
                self_href=self_href,
                title=title,
                version=version,
                service_desc_href=service_desc_href,
                extra_links=extra_links,
            )
        )
