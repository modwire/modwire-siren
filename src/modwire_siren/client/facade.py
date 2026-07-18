from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import urljoin, urlsplit

from .contracts import SirenResponse, SirenTransport
from .error import SirenClientError


class SirenClient:
    """Navigate Siren relations and execute only advertised actions."""

    def __init__(self, root_url: str, transport: SirenTransport):
        self.root_url = self._absolute_root(root_url)
        self._origin = self._url_origin(self.root_url)
        self._transport = transport

    async def root(self) -> dict[str, Any]:
        return await self._request("GET", self.root_url)

    async def follow(
        self,
        document: Mapping[str, Any],
        relation: str,
    ) -> dict[str, Any]:
        link = self._find(document, "links", "rel", relation)
        return await self._request("GET", self._target(link, f"link relation {relation!r}"))

    async def execute(
        self,
        document: Mapping[str, Any],
        action_name: str,
        payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        action = self.action(document, action_name)
        method = action.get("method", "GET")
        if not isinstance(method, str) or not method.strip():
            raise self._contract_error(f"Siren action {action_name!r} has an invalid method.")
        return await self._request(
            method.upper(),
            self._target(action, f"Siren action {action_name!r}"),
            payload,
        )

    def action(
        self,
        document: Mapping[str, Any],
        action_name: str,
    ) -> Mapping[str, Any]:
        return self._find(document, "actions", "name", action_name)

    async def collection_item(
        self,
        collection: Mapping[str, Any],
        identifier: Any,
        *,
        identifier_field: str = "id",
    ) -> dict[str, Any]:
        entities = self._sequence(collection, "entities")
        for entity in entities:
            if not isinstance(entity, Mapping):
                continue
            properties = entity.get("properties")
            if isinstance(properties, Mapping) and properties.get(identifier_field) == identifier:
                return await self.follow(entity, "self")
        raise SirenClientError(
            "item-not-found",
            f"No advertised collection item has {identifier_field!r} equal to {identifier!r}.",
            identifier_field=identifier_field,
            identifier=identifier,
        )

    async def _request(
        self,
        method: str,
        href: str,
        payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        target = self._same_origin(href)
        try:
            response = await self._transport.request(method, target, payload)
        except Exception as error:
            raise SirenClientError(
                "transport-error",
                "Siren transport request failed.",
                method=method,
                href=target,
            ) from error
        self._validate_response(response)
        if response.status_code >= 400:
            raise SirenClientError.problem(response.status_code, response.document)
        return dict(response.document)

    def _target(self, affordance: Mapping[str, Any], context: str) -> str:
        href = affordance.get("href")
        if not isinstance(href, str) or not href.strip():
            raise self._contract_error(f"{context} has no valid href.")
        return self._same_origin(href)

    def _same_origin(self, href: str) -> str:
        target = urljoin(self.root_url, href)
        if self._url_origin(target) != self._origin:
            raise SirenClientError(
                "cross-origin-target",
                "Siren target leaves the configured API origin.",
                href=target,
            )
        return target

    def _find(
        self,
        document: Mapping[str, Any],
        collection_name: str,
        field: str,
        expected: str,
    ) -> Mapping[str, Any]:
        for item in self._sequence(document, collection_name):
            if not isinstance(item, Mapping):
                continue
            value = item.get(field)
            if value == expected or self._contains(value, expected):
                return item
        raise SirenClientError(
            "affordance-not-found",
            f"Siren {field} {expected!r} is not advertised.",
            collection=collection_name,
            field=field,
            expected=expected,
        )

    def _sequence(
        self,
        document: Mapping[str, Any],
        field: str,
    ) -> Sequence[Any]:
        value = document.get(field, ())
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return value
        raise self._contract_error(f"Siren {field!r} is not a collection.")

    @staticmethod
    def _contains(value: Any, expected: str) -> bool:
        return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and expected in value

    @staticmethod
    def _validate_response(response: SirenResponse) -> None:
        if not isinstance(response, SirenResponse):
            raise SirenClientError(
                "invalid-transport-response",
                "Siren transport returned an invalid response contract.",
            )
        if not 100 <= response.status_code <= 599:
            raise SirenClientError(
                "invalid-transport-response",
                "Siren transport returned an invalid HTTP status code.",
                status=response.status_code,
            )

    @staticmethod
    def _absolute_root(root_url: str) -> str:
        origin = SirenClient._url_origin(root_url)
        if not origin[0] or not origin[1]:
            raise SirenClientError(
                "invalid-root-url",
                "Siren root URL must be absolute.",
                root_url=root_url,
            )
        return root_url

    @staticmethod
    def _url_origin(url: str) -> tuple[str, str, int | None]:
        parsed = urlsplit(url)
        scheme = parsed.scheme.casefold()
        return scheme, (parsed.hostname or "").casefold(), SirenClient._origin_port(scheme, parsed.port)

    @staticmethod
    def _origin_port(scheme: str, port: int | None) -> int | None:
        if port is not None:
            return port
        return {"http": 80, "https": 443}.get(scheme)

    @staticmethod
    def _contract_error(detail: str) -> SirenClientError:
        return SirenClientError("invalid-siren-contract", detail)
