from abc import ABC, abstractmethod
from typing import Any

from ..contracts.resource import SirenRelation, SirenResource
from ..profile.document import ProfileDocument
from ..standards import SirenOpenApiExtension
from .contracts import OpenApiResourceExtension


class OpenApiResourceSource(ABC):
    @abstractmethod
    def read(self, paths: dict[str, Any]) -> tuple[SirenResource, ...]:
        raise NotImplementedError


class OpenApiResourceReader(OpenApiResourceSource):
    def __init__(self, profiles: ProfileDocument):
        self._profiles = profiles

    def read(self, paths: dict[str, Any]) -> tuple[SirenResource, ...]:
        return tuple(
            self._resource(
                path,
                raw_extension,
                path_item.get(SirenOpenApiExtension.UI_PROFILE, {}),
            )
            for path, path_item in paths.items()
            if (raw_extension := path_item.get(SirenOpenApiExtension.RESOURCE))
        )

    def _resource(
        self,
        path: str,
        raw_extension: dict[str, Any],
        raw_profile: dict[str, Any],
    ) -> SirenResource:
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
            operations=extension.operations,
            collection_operations=extension.collection_operations,
            collection_only=extension.collection_only,
            singleton=extension.singleton,
            root_visible=extension.root_visible,
            profile=self._profiles.validate(raw_profile) if raw_profile else {},
        )
