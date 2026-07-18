from collections.abc import Callable
from typing import Any

CollectionOperationSelection = tuple[str, ...] | Callable[[Any, str], tuple[str, ...]]


class SirenCollectionPolicyResolver:
    def operations(
        self,
        policy: Any,
        selection: CollectionOperationSelection,
        request: Any,
        resource_name: str,
    ) -> tuple[str, ...]:
        if hasattr(policy, "operations_for_collection"):
            method = policy.operations_for_collection
            if not callable(method):
                raise ValueError("Siren policy operations_for_collection must be callable")
            return tuple(method(request, resource_name))
        if callable(selection):
            return tuple(selection(request, resource_name))
        return tuple(selection)
