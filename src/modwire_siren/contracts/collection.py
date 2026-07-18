from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class PaginationLinkInput:
    """Describe one collection pagination link relative to the collection path."""

    rel: str
    query: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class NoPagination:
    """Use the current collection path as the only collection link."""


@dataclass(frozen=True, slots=True)
class OffsetPagination:
    """Create standard offset pagination links for a collection."""

    limit: int
    offset: int
    count: int
    has_next: bool


@dataclass(frozen=True, slots=True)
class CustomPagination:
    """Use application-provided collection pagination links."""

    count: int
    links: tuple[PaginationLinkInput, ...]


@dataclass(frozen=True, slots=True)
class SirenCollectionRequest:
    """Describe resource items and controls projected into one Siren collection."""

    resource_name: str
    items: Sequence[Mapping[str, Any]]
    collection_operation_ids: tuple[str, ...]
    item_operation_ids: tuple[str, ...]
    path_values: Mapping[str, Any]
    pagination: NoPagination | OffsetPagination | CustomPagination = NoPagination()
