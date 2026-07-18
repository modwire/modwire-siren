from copy import deepcopy
from typing import Any

from ..standards import SirenOpenApiExtension
from .path_template_validator import OpenApiPathTemplateValidator
from .resource_spec import SirenResourceSpec
from .resource_spec_serializer import SirenResourceSpecSerializer
from .resource_validator import SirenResourceValidator


class SirenResourceInjector:
    def __init__(
        self,
        serializer: SirenResourceSpecSerializer,
        paths: OpenApiPathTemplateValidator,
        validator: SirenResourceValidator,
    ):
        self._serializer = serializer
        self._paths = paths
        self._validator = validator

    def inject(self, schema: dict[str, Any], resources: tuple[SirenResourceSpec, ...]) -> dict[str, Any]:
        document = deepcopy(schema)
        paths = document.setdefault("paths", {})
        for resource in resources:
            self._paths.validate(resource.path)
            if resource.path not in paths:
                raise ValueError(f"Siren resource path is not present in OpenAPI schema: {resource.path}")
            extension = self._serializer.serialize(resource)
            existing = paths[resource.path].get(SirenOpenApiExtension.RESOURCE)
            if existing is not None and existing != extension:
                raise ValueError(f"Siren resource path already has different metadata: {resource.path}")
            paths[resource.path][SirenOpenApiExtension.RESOURCE] = extension
        self._validator.validate(document, tuple(resource.name for resource in resources))
        return document
