from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

PaginationQuery = Mapping[str, Any] | Sequence[tuple[str, Any]]


@dataclass(frozen=True, slots=True)
class PaginationLinkInput:

    rel: str
    query: PaginationQuery


@dataclass(frozen=True, slots=True)
class NoPagination:


@dataclass(frozen=True, slots=True)
class OffsetPagination:

    limit: int
    offset: int
    count: int
    has_next: bool


@dataclass(frozen=True, slots=True)
class CustomPagination:

    count: int
    links: tuple[PaginationLinkInput, ...]


DEFAULT_PAGINATION = NoPagination()


@dataclass(frozen=True, slots=True)
class SirenCollectionRequest:

    resource_name: str
    items: Sequence[Mapping[str, Any]]
    collection_operation_ids: tuple[str, ...]
    item_operation_ids: tuple[str, ...]
    path_values: Mapping[str, Any]
    pagination: NoPagination | OffsetPagination | CustomPagination = DEFAULT_PAGINATION
    query: PaginationQuery = ()
