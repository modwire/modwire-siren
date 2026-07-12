from typing import Any

from .catalog import OpenApiCatalog
from .operation import OpenApiOperationReader
from .resolver import ComponentSchemaResolver
from .resource import OpenApiResourceSource


class OpenApiCatalogFactory:
    def __init__(self, resources: OpenApiResourceSource):
        self._resources = resources

    def create(self, schema: dict[str, Any]) -> OpenApiCatalog:
        components = schema.get("components", {}).get("schemas", {})
        paths = schema.get("paths", {})
        operations = OpenApiOperationReader(ComponentSchemaResolver(components)).read(paths)
        resources = self._resources.read(paths)
        return OpenApiCatalog(operations, resources)
