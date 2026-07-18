from typing import Any

from ..profile.document import ProfileDocument
from ..profile.standard import ProfileStandard
from .factory import OpenApiCatalogFactory
from .resource import OpenApiResourceReader


class SirenResourceValidator:
    def validate(self, schema: dict[str, Any], resource_names: tuple[str, ...] = ()) -> None:
        profiles = ProfileDocument(ProfileStandard.load())
        catalog = OpenApiCatalogFactory(OpenApiResourceReader(profiles)).create(schema)
        for resource_name in resource_names:
            catalog.resource(resource_name)
