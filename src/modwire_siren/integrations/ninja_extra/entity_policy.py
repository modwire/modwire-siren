from collections.abc import Callable, Mapping
from typing import Any

from ...contracts.related_link import RelatedLinkInput

EntityOperationSelection = tuple[str, ...] | Callable[[Any, Mapping[str, Any]], tuple[str, ...]]
EntityRelatedLinkSelection = (
    tuple[RelatedLinkInput, ...] | Callable[[Any, Mapping[str, Any]], tuple[RelatedLinkInput, ...]]
)


class SirenEntityPolicyResolver:
    def operations(
        self,
        policy: Any,
        selection: EntityOperationSelection,
        request: Any,
        resource_name: str,
        properties: Mapping[str, Any],
    ) -> tuple[str, ...]:
        if hasattr(policy, "operations_for_entity"):
            method = policy.operations_for_entity
            if not callable(method):
                raise ValueError("Siren policy operations_for_entity must be callable")
            return tuple(method(request, resource_name, properties))
        if callable(selection):
            return tuple(selection(request, properties))
        return tuple(selection)

    def related_links(
        self,
        policy: Any,
        selection: EntityRelatedLinkSelection,
        request: Any,
        resource_name: str,
        properties: Mapping[str, Any],
    ) -> tuple[RelatedLinkInput, ...]:
        if hasattr(policy, "related_links_for_entity"):
            method = policy.related_links_for_entity
            if not callable(method):
                raise ValueError("Siren policy related_links_for_entity must be callable")
            return tuple(method(request, resource_name, properties))
        if callable(selection):
            return tuple(selection(request, properties))
        return tuple(selection)
