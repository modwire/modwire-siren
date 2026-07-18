import re
from collections.abc import Mapping
from typing import Any

from ..contracts.resource import SirenResource
from ..contracts.root import SirenRootRequest
from ..openapi.catalog import SirenResourceCatalog
from ..openapi.error import OpenApiError
from ..openapi.href import SirenHrefResolver
from ..standards import SirenMediaType


class SirenRootFactory:
    def __init__(self, catalog: SirenResourceCatalog, hrefs: SirenHrefResolver):
        self._catalog = catalog
        self._hrefs = hrefs

    def create(self, request: SirenRootRequest) -> dict[str, Any]:
        properties = {
            key: value
            for key, value in {
                "title": request.title,
                "version": request.version,
            }.items()
            if value
        }
        links: list[dict[str, Any]] = [{"rel": ["self"], "href": request.self_href}]
        links.extend(self._collection_links())
        if request.service_desc_href:
            links.append(
                {
                    "rel": ["service-desc"],
                    "href": request.service_desc_href,
                    "type": SirenMediaType.OPENAPI,
                }
            )
        links.extend(self._extra_link(link) for link in request.extra_links)
        return {
            "class": ["api", "entry-point"],
            "properties": properties,
            "links": links,
            "actions": [],
            "entities": [],
        }

    def _collection_links(self) -> tuple[dict[str, Any], ...]:
        operation_paths = {operation.path for operation in self._catalog.operations()}
        links: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()
        for resource in self._catalog.resources():
            if not self._root_visible(resource):
                continue
            path = self._collection_path(resource, operation_paths)
            if not path:
                continue
            link = (
                self._collection_relation(resource, path),
                self._hrefs.resolve(path, {}),
            )
            if link in seen:
                continue
            seen.add(link)
            rel, href = link
            links.append({"rel": [rel], "href": href, "type": SirenMediaType.ENTITY})
        return tuple(links)

    def _collection_path(self, resource: SirenResource, operation_paths: set[str]) -> str:
        path = resource.path if resource.collection_only or resource.singleton else self._parent_path(resource.path)
        if path not in operation_paths or self._has_placeholders(path):
            return ""
        return path

    @staticmethod
    def _root_visible(resource: SirenResource) -> bool:
        if resource.root_visible is not None:
            return resource.root_visible
        return not resource.singleton

    @staticmethod
    def _parent_path(path: str) -> str:
        parent = path.rstrip("/").rsplit("/", 1)[0]
        return parent or "/"

    @staticmethod
    def _collection_relation(resource: SirenResource, path: str) -> str:
        segment = path.rstrip("/").rsplit("/", 1)[-1]
        return segment or resource.name

    @staticmethod
    def _has_placeholders(path: str) -> bool:
        return bool(re.search(r"{[^}]+}", path))

    @staticmethod
    def _extra_link(link: Mapping[str, Any]) -> dict[str, Any]:
        if "rel" not in link or "href" not in link:
            raise OpenApiError("Root extra links require rel and href")
        return dict(link)
