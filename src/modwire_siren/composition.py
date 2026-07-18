from collections.abc import Callable
from typing import Any

from .facade import ModwireSiren
from .factories.action import SirenActionFactory
from .factories.collection import SirenCollectionFactory
from .factories.entity import SirenEntityFactory
from .factories.field import OpenApiSirenFieldFactory
from .factories.link import OpenApiSirenLinkFactory
from .factories.pagination import SirenCollectionPaginationFactory, SirenPaginationHrefFactory
from .factories.related_link import SirenRelatedLinkFactory
from .factories.resource import OpenApiSirenResourceHrefResolver
from .factories.root import SirenRootFactory
from .openapi.factory import OpenApiCatalogFactory
from .openapi.href import OpenApiHrefResolver
from .openapi.resource import OpenApiResourceReader
from .policies.field_type import OpenApiSirenFieldTypeResolver
from .profile.document import ProfileDocument
from .profile.projection import ProfileProjector
from .profile.standard import ProfileStandard
from .serialization import PydanticSirenSerializer

BaseUrlResolver = str | Callable[[Any], str]


class ModwireSirenFactory:
    """Build the standard OpenAPI-backed Siren façade."""

    @classmethod
    def standard(cls, schema: dict[str, Any], base_url: str) -> ModwireSiren:
        """Create a ready-to-use façade from an OpenAPI schema and API base URL."""
        profiles = ProfileDocument(ProfileStandard.load())
        catalog = OpenApiCatalogFactory(OpenApiResourceReader(profiles)).create(schema)
        hrefs = OpenApiHrefResolver(base_url)
        resource_hrefs = OpenApiSirenResourceHrefResolver(hrefs)
        fields = OpenApiSirenFieldFactory(OpenApiSirenFieldTypeResolver())
        actions = SirenActionFactory(catalog, hrefs, fields)
        links = OpenApiSirenLinkFactory(catalog, resource_hrefs)
        related_links = SirenRelatedLinkFactory(catalog, resource_hrefs)
        profile_projector = ProfileProjector(profiles)
        entities = SirenEntityFactory(catalog, resource_hrefs, links, related_links, actions, profile_projector)
        collections = SirenCollectionFactory(
            catalog,
            hrefs,
            entities,
            actions,
            SirenPaginationHrefFactory(),
            SirenCollectionPaginationFactory(),
        )
        roots = SirenRootFactory(catalog, hrefs)
        return ModwireSiren(entities, collections, roots, PydanticSirenSerializer())

    @classmethod
    def web(cls, schema: dict[str, Any], *, base_url_resolver: BaseUrlResolver) -> "RequestAwareModwireSirenFactory":
        """Create a request-aware factory for web integrations."""
        return RequestAwareModwireSirenFactory(schema, base_url_resolver)


class RequestAwareModwireSirenFactory:
    """Build Siren façades from the current web request."""

    def __init__(self, schema: dict[str, Any], base_url_resolver: BaseUrlResolver):
        self._schema = schema
        self._base_url_resolver = base_url_resolver

    def for_request(self, request: Any) -> ModwireSiren:
        resolver = self._base_url_resolver
        base_url = resolver(request) if callable(resolver) else resolver
        return ModwireSirenFactory.standard(self._schema, base_url)
