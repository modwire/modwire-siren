from abc import ABC, abstractmethod
from typing import Any

from ..contracts.resource import SirenRelation, SirenResource
from ..standards import SirenOpenApiExtension
from .contracts import OpenApiResourceExtension


class OpenApiResourceSource(ABC):
    @abstractmethod
    def read(self, paths: dict[str, Any]) -> tuple[SirenResource, ...]:
        raise NotImplementedError


class OpenApiResourceReader(OpenApiResourceSource):
    def read(self, paths: dict[str, Any]) -> tuple[SirenResource, ...]:
        return tuple(
            self._resource(path, raw_extension)
            for path, path_item in paths.items()
            if (raw_extension := path_item.get(SirenOpenApiExtension.RESOURCE))
        )

    def _resource(self, path: str, raw_extension: dict[str, Any]) -> SirenResource:
        extension = OpenApiResourceExtension.model_validate(raw_extension)
        return SirenResource(
            name=extension.name,
            path=path,
            resource_class=extension.resource_class,
            identifier=extension.identifier,
            path_parameters=extension.path_parameters,
            relations=tuple(
                SirenRelation(field=field, **relation.model_dump()) for field, relation in extension.relations.items()
            ),
        )
