from typing import Any

from .facade import ModwireSiren
from .factories.action import SirenActionFactory
from .factories.entity import SirenEntityFactory
from .factories.field import OpenApiSirenFieldFactory
from .factories.link import OpenApiSirenLinkFactory
from .factories.resource import OpenApiSirenResourceHrefResolver
from .openapi.factory import OpenApiCatalogFactory
from .openapi.href import OpenApiHrefResolver
from .openapi.resource import OpenApiResourceReader
from .policies.field_type import OpenApiSirenFieldTypeResolver
from .profile.document import ProfileDocument
from .profile.projection import ProfileProjector
from .profile.standard import ProfileStandard
from .serialization import PydanticSirenSerializer


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
        profile_projector = ProfileProjector(profiles)
        entities = SirenEntityFactory(catalog, resource_hrefs, links, actions, profile_projector)
        return ModwireSiren(entities, PydanticSirenSerializer())
