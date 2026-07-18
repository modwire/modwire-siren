from collections.abc import Iterable, Mapping
from typing import Any

from ..contracts.link import SirenLink
from ..contracts.related_link import RelatedLinkInput
from ..openapi.catalog import SirenResourceCatalog
from ..openapi.error import OpenApiError
from ..standards import SirenMediaType
from .resource import SirenResourceHrefResolver


class SirenRelatedLinkFactory:
    def __init__(self, catalog: SirenResourceCatalog, hrefs: SirenResourceHrefResolver):
        self._catalog = catalog
        self._hrefs = hrefs

    def create(self, inputs: tuple[RelatedLinkInput, ...]) -> tuple[SirenLink, ...]:
        return tuple(link for related in inputs for link in self.links(related))

    def links(self, related: RelatedLinkInput) -> tuple[SirenLink, ...]:
        target = self._catalog.resource(related.resource)
        return tuple(
            SirenLink(
                rel=(related.rel,),
                href=self._hrefs.href(target, {target.identifier: value}),
                title=related.rel,
                media_type=SirenMediaType.ENTITY,
            )
            for value in self.values(related)
        )

    def values(self, related: RelatedLinkInput) -> tuple[Any, ...]:
        value = related.value
        if value is None:
            raise OpenApiError(f"Related link {related.rel!r} requires a non-null value")
        if isinstance(value, (str, bytes, Mapping)) or not isinstance(value, Iterable):
            return (value,)
        values = tuple(value)
        if any(item is None for item in values):
            raise OpenApiError(f"Related link {related.rel!r} requires non-null values")
        return values
