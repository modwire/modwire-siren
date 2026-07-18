import asyncio
from collections.abc import Mapping
from typing import Any

import pytest

from modwire_siren import SirenClient, SirenClientError, SirenResponse


class RecordingTransport:
    def __init__(self, responses: Mapping[tuple[str, str], SirenResponse]):
        self.responses = responses
        self.requests: list[tuple[str, str, Mapping[str, Any] | None]] = []

    async def request(
        self,
        method: str,
        href: str,
        payload: Mapping[str, Any] | None = None,
    ) -> SirenResponse:
        self.requests.append((method, href, payload))
        return self.responses[method, href]


class FailingTransport:
    async def request(
        self,
        method: str,
        href: str,
        payload: Mapping[str, Any] | None = None,
    ) -> SirenResponse:
        raise TimeoutError("request timed out")


def test_client_follows_relative_relations_and_discovers_collection_items():
    transport = RecordingTransport(
        {
            ("GET", "https://api.test/root"): SirenResponse(
                status_code=200,
                document={"links": [{"rel": ["records"], "href": "/records"}]},
            ),
            ("GET", "https://api.test/records"): SirenResponse(
                status_code=200,
                document={
                    "entities": [
                        {
                            "properties": {"id": "architecture"},
                            "links": [{"rel": ["self"], "href": "/records/architecture"}],
                        }
                    ]
                },
            ),
            ("GET", "https://api.test/records/architecture"): SirenResponse(
                status_code=200,
                document={"properties": {"id": "architecture"}},
            ),
        }
    )
    client = SirenClient("https://api.test/root", transport)

    async def scenario():
        collection = await client.follow(await client.root(), "records")
        return await client.collection_item(collection, "architecture")

    item = asyncio.run(scenario())

    assert item["properties"] == {"id": "architecture"}
    assert transport.requests == [
        ("GET", "https://api.test/root", None),
        ("GET", "https://api.test/records", None),
        ("GET", "https://api.test/records/architecture", None),
    ]


def test_client_executes_only_the_advertised_action():
    response = SirenResponse(
        status_code=200,
        document={"properties": {"updated": True}},
    )
    transport = RecordingTransport({("PATCH", "https://api.test/records/architecture"): response})
    client = SirenClient("https://api.test/root", transport)
    entity = {
        "actions": [
            {
                "name": "revise_record",
                "method": "patch",
                "href": "/records/architecture",
            }
        ]
    }

    result = asyncio.run(client.execute(entity, "revise_record", {"title": "Architecture"}))

    assert result == {"properties": {"updated": True}}
    assert transport.requests == [
        (
            "PATCH",
            "https://api.test/records/architecture",
            {"title": "Architecture"},
        )
    ]


def test_client_preserves_structured_remote_problem_details():
    transport = RecordingTransport(
        {
            ("POST", "https://api.test/records"): SirenResponse(
                status_code=422,
                document={
                    "title": "Validation failed",
                    "detail": "title is required",
                    "errors": [{"field": "title", "code": "required"}],
                },
            )
        }
    )
    client = SirenClient("https://api.test/root", transport)

    with pytest.raises(SirenClientError) as raised:
        asyncio.run(
            client.execute(
                {
                    "actions": [
                        {
                            "name": "create_record",
                            "method": "POST",
                            "href": "/records",
                        }
                    ]
                },
                "create_record",
                {},
            )
        )

    assert raised.value.as_dict() == {
        "kind": "remote-problem",
        "detail": "title is required",
        "status": 422,
        "title": "Validation failed",
        "body": {
            "title": "Validation failed",
            "detail": "title is required",
            "errors": [{"field": "title", "code": "required"}],
        },
    }


@pytest.mark.parametrize(
    ("document", "operation", "kind"),
    (
        ({"links": []}, "follow", "affordance-not-found"),
        ({"actions": []}, "execute", "affordance-not-found"),
        ({"entities": {}}, "collection", "invalid-siren-contract"),
    ),
)
def test_client_reports_missing_or_malformed_affordances(document, operation, kind):
    client = SirenClient("https://api.test/root", RecordingTransport({}))

    with pytest.raises(SirenClientError) as raised:
        if operation == "follow":
            asyncio.run(client.follow(document, "records"))
        elif operation == "execute":
            asyncio.run(client.execute(document, "create_record"))
        else:
            asyncio.run(client.collection_item(document, "architecture"))

    assert raised.value.kind == kind


@pytest.mark.parametrize(
    "operation",
    ("follow", "execute"),
)
def test_client_rejects_cross_origin_targets(operation):
    client = SirenClient("https://api.test/root", RecordingTransport({}))

    with pytest.raises(SirenClientError) as raised:
        if operation == "follow":
            asyncio.run(
                client.follow(
                    {"links": [{"rel": ["records"], "href": "https://evil.test/records"}]},
                    "records",
                )
            )
        else:
            asyncio.run(
                client.execute(
                    {
                        "actions": [
                            {
                                "name": "create_record",
                                "href": "https://evil.test/records",
                            }
                        ]
                    },
                    "create_record",
                )
            )

    assert raised.value.kind == "cross-origin-target"


def test_client_accepts_same_origin_links_with_default_https_port():
    transport = RecordingTransport(
        {
            ("GET", "https://api.test:443/records"): SirenResponse(
                status_code=200,
                document={"class": ["collection"]},
            ),
        }
    )
    client = SirenClient("https://api.test/root", transport)

    document = asyncio.run(
        client.follow(
            {"links": [{"rel": ["records"], "href": "https://api.test:443/records"}]},
            "records",
        )
    )

    assert document == {"class": ["collection"]}
    assert transport.requests == [("GET", "https://api.test:443/records", None)]


def test_client_reports_transport_failures_with_public_error_contract():
    client = SirenClient("https://api.test/root", FailingTransport())

    with pytest.raises(SirenClientError) as raised:
        asyncio.run(client.root())

    assert raised.value.as_dict() == {
        "kind": "transport-error",
        "detail": "Siren transport request failed.",
        "method": "GET",
        "href": "https://api.test/root",
    }
    assert isinstance(raised.value.__cause__, TimeoutError)
