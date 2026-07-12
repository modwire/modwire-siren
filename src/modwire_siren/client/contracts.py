from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from ..contracts.base import SirenContract


class SirenResponse(SirenContract):
    """Carry one transport response without coupling Siren to an HTTP library."""

    status_code: int
    document: dict[str, Any]


class SirenTransport(Protocol):
    """Execute Siren requests for a client-owned transport lifecycle."""

    async def request(
        self,
        method: str,
        href: str,
        payload: Mapping[str, Any] | None = None,
    ) -> SirenResponse: ...
