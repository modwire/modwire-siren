from typing import Protocol, runtime_checkable

from pydantic import JsonValue

from ..values import SirenAdapterPolicy


@runtime_checkable
class SirenCapabilityPolicy(Protocol):
    """Select application authorization and optional projection overrides for one response."""

    def select(
        self, operation_id: str | None, status: int, request: object, result: JsonValue
    ) -> SirenAdapterPolicy: ...
