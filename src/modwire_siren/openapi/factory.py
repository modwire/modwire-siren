from typing import Any

from .catalog import OpenApiCatalog
from .operation import OpenApiOperationReader
from .resolver import ComponentSchemaResolver
from .resource import OpenApiResourceReader


class OpenApiCatalogFactory:
    @classmethod
    def create(cls, schema: dict[str, Any]) -> OpenApiCatalog:
        components = schema.get("components", {}).get("schemas", {})
        paths = schema.get("paths", {})
        operations = OpenApiOperationReader(ComponentSchemaResolver(components)).read(paths)
        resources = OpenApiResourceReader().read(paths)
        return OpenApiCatalog(operations, resources)
