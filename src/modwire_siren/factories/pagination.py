from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from ..contracts.collection import CustomPagination, NoPagination, OffsetPagination, PaginationLinkInput
from ..standards import SirenRelationName


class SirenPaginationHrefFactory:
    def create(self, base_href: str, link: PaginationLinkInput) -> str:
        parts = urlsplit(base_href)
        query = dict(parse_qsl(parts.query, keep_blank_values=True))
        query.update({name: str(value) for name, value in link.query.items()})
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


class SirenCollectionPaginationFactory:
    def validate(self, pagination: NoPagination | OffsetPagination | CustomPagination) -> None:
        if isinstance(pagination, OffsetPagination):
            if pagination.limit <= 0:
                raise ValueError("Offset pagination limit must be greater than zero")
            if pagination.offset < 0:
                raise ValueError("Offset pagination offset must not be negative")
            if pagination.count < 0:
                raise ValueError("Offset pagination count must not be negative")
        if isinstance(pagination, CustomPagination):
            if pagination.count < 0:
                raise ValueError("Custom pagination count must not be negative")
            if not pagination.links:
                raise ValueError("Custom pagination links must not be empty")
            if not any(link.rel == SirenRelationName.SELF for link in pagination.links):
                raise ValueError("Custom pagination links must include a self link")

    def count(self, pagination: NoPagination | OffsetPagination | CustomPagination, item_count: int) -> int:
        if isinstance(pagination, OffsetPagination | CustomPagination):
            return pagination.count
        return item_count

    def links(self, pagination: NoPagination | OffsetPagination | CustomPagination) -> tuple[PaginationLinkInput, ...]:
        if isinstance(pagination, OffsetPagination):
            links = [
                PaginationLinkInput(rel="self", query={"limit": pagination.limit, "offset": pagination.offset}),
                PaginationLinkInput(rel="first", query={"limit": pagination.limit, "offset": 0}),
            ]
            if pagination.offset > 0:
                links.append(
                    PaginationLinkInput(
                        rel="previous",
                        query={"limit": pagination.limit, "offset": max(pagination.offset - pagination.limit, 0)},
                    )
                )
            if pagination.has_next:
                links.append(
                    PaginationLinkInput(
                        rel="next",
                        query={"limit": pagination.limit, "offset": pagination.offset + pagination.limit},
                    )
                )
            return tuple(links)
        if isinstance(pagination, CustomPagination):
            return pagination.links
        return (PaginationLinkInput(rel="self", query={}),)
