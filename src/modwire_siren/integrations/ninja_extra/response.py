from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any

from ...standards import SirenMediaType


class EmptyMapping(Mapping[str, Any]):
    """Immutable empty mapping for non-null default arguments."""

    def __getitem__(self, key: str) -> Any:
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return iter(())

    def __len__(self) -> int:
        return 0

    def __repr__(self) -> str:
        return "{}"


EMPTY_HEADERS: Mapping[str, str] = EmptyMapping()
EMPTY_VALUES: Mapping[str, Any] = EmptyMapping()


@dataclass(frozen=True, slots=True)
class NinjaExtraSirenResponse:
    """Framework-light response payload for Ninja Extra adapters."""

    body: dict[str, Any] | None
    status_code: int = 200
    headers: dict[str, str] = field(default_factory=dict)
    content_type: str | None = SirenMediaType.ENTITY


class NinjaExtraSirenResponseFactory:
    def create(
        self,
        body: dict[str, Any] | None,
        *,
        status_code: int,
        headers: Mapping[str, str],
        content_type: str | None,
    ) -> NinjaExtraSirenResponse:
        if any(name.lower() == "content-type" for name in headers):
            raise ValueError("Pass response media type through content_type, not headers")
        return NinjaExtraSirenResponse(
            body=body,
            status_code=status_code,
            headers=dict(headers),
            content_type=content_type,
        )
