from typing import Protocol, runtime_checkable

from pydantic import JsonValue

from ..values import SirenAdapterPolicy


@runtime_checkable
class SirenCapabilityPolicy(Protocol):
    """Select explicit application capabilities and projection semantics for one response."""

    def select(
        self, operation_id: str | None, status: int, request: object, result: JsonValue
    ) -> SirenAdapterPolicy: ...
