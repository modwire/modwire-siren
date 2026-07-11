from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
from typing import Any

from ..contracts.link import SirenLink
from ..contracts.resource import SirenRelation, SirenResource
from ..openapi.catalog import SirenResourceCatalog
from ..openapi.error import OpenApiError
from ..standards import SirenMediaType, SirenRelationName
from .resource import SirenResourceHrefResolver


class SirenLinkFactory(ABC):
    @abstractmethod
    def create(self, resource: SirenResource, properties: Mapping[str, Any]) -> tuple[SirenLink, ...]:
        raise NotImplementedError


class OpenApiSirenLinkFactory(SirenLinkFactory):
    def __init__(self, catalog: SirenResourceCatalog, hrefs: SirenResourceHrefResolver):
        self._catalog = catalog
        self._hrefs = hrefs

    def create(self, resource: SirenResource, properties: Mapping[str, Any]) -> tuple[SirenLink, ...]:
        return (self._self_link(resource, properties), *self._relation_links(resource, properties))

    def _self_link(self, resource: SirenResource, properties: Mapping[str, Any]) -> SirenLink:
        return SirenLink(
            rel=(SirenRelationName.SELF,),
            href=self._hrefs.href(resource, properties),
            title=resource.resource_class,
            media_type=SirenMediaType.ENTITY,
        )

    def _relation_links(self, resource: SirenResource, properties: Mapping[str, Any]) -> tuple[SirenLink, ...]:
        return tuple(
            self._relation_link(relation, value)
            for relation in resource.relations
            if relation.field in properties
            for value in self._relation_values(relation, properties[relation.field])
        )

    def _relation_link(self, relation: SirenRelation, value: Any) -> SirenLink:
        target = self._catalog.resource(relation.resource)
        return SirenLink(
            rel=(relation.rel,),
            href=self._hrefs.href(target, {target.identifier: value}),
            title=relation.rel,
            media_type=SirenMediaType.ENTITY,
        )

    def _relation_values(self, relation: SirenRelation, value: Any) -> tuple[Any, ...]:
        if value is None:
            raise OpenApiError(f"Relation {relation.rel!r} requires a non-null value")
        if relation.many:
            if isinstance(value, (str, bytes, Mapping)) or not isinstance(value, Iterable):
                raise OpenApiError(f"Relation {relation.rel!r} requires an iterable value")
            values = tuple(value)
            if any(item is None for item in values):
                raise OpenApiError(f"Relation {relation.rel!r} requires non-null values")
            return values
        return (value,)
