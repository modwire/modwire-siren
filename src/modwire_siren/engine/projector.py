import re
from collections.abc import Mapping
from typing import Any
from urllib.parse import quote

from ..contracts import SirenApi, SirenContext, SirenOperation, SirenResource

_PARAMETER = re.compile(r"\{([^}]+)\}")


class SirenEngine:
    def __init__(self, api: SirenApi):
        self._api = api
        self._resources: dict[str, list[SirenResource]] = {}
        for resource in api.resources:
            self._resources.setdefault(resource.name, []).append(resource)
        self._operations = {operation.name: operation for operation in api.operations}

    def project(self, context: SirenContext) -> dict[str, Any]:
        if context.scope == "root":
            return self._root(context)
        resource = self._resource(context)
        self._validate_capabilities(resource, context)
        if context.scope == "collection":
            return self._collection(resource, context)
        return self._entity(resource, context.value, context, ())

    def _root(self, context: SirenContext) -> dict[str, Any]:
        links = [{"rel": ["self"], "href": self._href(self._api.root.route.path, context, None)}]
        links.extend(
            {
                "rel": [resource.name],
                "href": self._href(resource.collection.path, context, resource, include_query=False),
            }
            for resource in self._api.resources
            if not _PARAMETER.search(resource.collection.path)
        )
        return {"class": ["api", "entry-point"], "links": links}

    def _collection(self, resource: SirenResource, context: SirenContext) -> dict[str, Any]:
        return {
            "class": ["collection", resource.resource_class],
            "properties": dict(context.value),
            "entities": [self._entity(resource, item, context, ("item",)) for item in context.items],
            "actions": self._actions(resource, "collection", context, context.value),
            "links": [{"rel": ["self"], "href": self._href(resource.collection.path, context, resource)}],
        }

    def _entity(
        self,
        resource: SirenResource,
        value: Mapping[str, Any],
        context: SirenContext,
        rel: tuple[str, ...],
    ) -> dict[str, Any]:
        document: dict[str, Any] = {
            "class": [resource.resource_class],
            "properties": dict(value),
            "actions": self._actions(resource, "entity", context, value),
            "links": [
                {
                    "rel": ["self"],
                    "href": self._href(
                        resource.entity.path if resource.entity else resource.collection.path,
                        context,
                        resource,
                        value,
                    ),
                }
            ],
        }
        if rel:
            document["rel"] = list(rel)
        return document

    def _actions(
        self,
        resource: SirenResource,
        scope: str,
        context: SirenContext,
        value: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        names = resource.collection_operations if scope == "collection" else resource.entity_operations
        return [
            self._action(self._operations[name], context, resource, value)
            for name in names
            if name in context.capabilities
        ]

    def _action(
        self,
        operation: SirenOperation,
        context: SirenContext,
        resource: SirenResource,
        value: Mapping[str, Any],
    ) -> dict[str, Any]:
        action: dict[str, Any] = {
            "name": operation.name,
            "href": self._href(operation.route.path, context, resource, value),
            "method": operation.method,
        }
        if operation.fields:
            action["fields"] = [
                {
                    "name": field.name,
                    "type": field.definition.get("type", "text"),
                    "required": field.required,
                }
                for field in operation.fields
            ]
        return action

    def _resource(self, context: SirenContext) -> SirenResource:
        if context.resource is None:
            raise ValueError(f"Siren {context.scope} context requires a resource")
        candidates = self._resources.get(context.resource)
        if candidates is None:
            raise ValueError(f"Siren context references unknown resource: {context.resource}")
        if len(candidates) == 1:
            return candidates[0]
        values = set(context.value) | set(context.path_values)
        matches = [
            resource
            for resource in candidates
            if set(_PARAMETER.findall(resource.collection.path)).issubset(values)
        ]
        if not matches:
            raise ValueError(f"Siren context cannot select resource {context.resource!r}: provide parent path values")
        longest = max(len(_PARAMETER.findall(resource.collection.path)) for resource in matches)
        selected = [resource for resource in matches if len(_PARAMETER.findall(resource.collection.path)) == longest]
        if len(selected) != 1:
            raise ValueError(
                f"Siren context cannot select resource {context.resource!r}: matching routes are ambiguous"
            )
        return selected[0]

    @staticmethod
    def _validate_capabilities(resource: SirenResource, context: SirenContext) -> None:
        supported = set(resource.collection_operations) | set(resource.entity_operations)
        unknown = sorted(context.capabilities - supported)
        if unknown:
            raise ValueError(f"Siren context declares unsupported capabilities for {resource.name!r}: {unknown}")

    @staticmethod
    def _href(
        path: str,
        context: SirenContext,
        resource: SirenResource | None,
        value: Mapping[str, Any] | None = None,
        include_query: bool = True,
    ) -> str:
        values = dict(context.value)
        values.update(context.path_values)
        values.update(value or {})

        def replace(match: re.Match[str]) -> str:
            parameter = match.group(1)
            path_value = values.get(parameter)
            if path_value is None and resource is not None:
                path_value = values.get(resource.identifier)
            if path_value is None:
                raise ValueError(f"Siren link requires path value: {parameter}")
            return quote(str(path_value), safe="")

        href = f"{context.base_url.rstrip('/')}{_PARAMETER.sub(replace, path)}"
        if not include_query or not context.query:
            return href
        query_items = []
        for name, query_value in context.query:
            if query_value is None:
                value = ""
            elif isinstance(query_value, bool):
                value = str(query_value).lower()
            else:
                value = str(query_value)
            query_items.append(f"{quote(name, safe='')}={quote(value, safe='')}")
        query = "&".join(query_items)
        return f"{href}?{query}"
