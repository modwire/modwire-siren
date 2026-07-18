from dataclasses import dataclass, field
from typing import Any

from ...standards import SirenMediaType


@dataclass(frozen=True, slots=True)
class NinjaExtraSirenResponse:
    """Framework-light response payload for Ninja Extra adapters."""

    body: dict[str, Any] | None
    status_code: int = 200
    headers: dict[str, str] = field(default_factory=dict)
    content_type: str | None = SirenMediaType.ENTITY
