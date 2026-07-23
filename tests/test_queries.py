import pytest
from openapi_documents import ROUTE_POLICY_SCHEMA, SCHEMA

from modwire_siren import SirenContext, siren


def test_public_facade_serializes_ordered_repeated_and_escaped_query_values():
    document = siren(SCHEMA).project(
        SirenContext(
            base_url="https://api.example.com",
            scope="collection",
            resource="record",
            query=(
                ("filter", "a/b & c"),
                ("tag", "first"),
                ("tag", "second"),
                ("empty", ""),
                ("missing", None),
                ("ż", "✓"),
            ),
            capabilities=frozenset({"list_records"}),
        )
    )

    href = (
        "https://api.example.com/records?filter=a%2Fb%20%26%20c&tag=first&tag=second&empty=&missing=&%C5%BC=%E2%9C%93"
    )
    assert document["links"] == [{"rel": ["self"], "href": href}]
    assert document["actions"] == [{"name": "list_records", "href": href, "method": "GET"}]


def test_public_facade_limits_root_query_values_to_the_self_link():
    document = siren(SCHEMA).project(
        SirenContext(base_url="https://api.example.com", scope="root", query=(("format", "siren"),))
    )

    assert document["links"] == [
        {"rel": ["self"], "href": "https://api.example.com/?format=siren"},
        {"rel": ["record"], "href": "https://api.example.com/records"},
    ]


def test_public_facade_rejects_nonscalar_query_values_and_recovers():
    with pytest.raises(ValueError, match="Siren query values must be scalar"):
        SirenContext(base_url="https://api.example.com", scope="root", query=(("tag", ["one", "two"]),))

    with pytest.raises(ValueError, match="Siren link requires path value: team"):
        siren(ROUTE_POLICY_SCHEMA).project(
            SirenContext(
                base_url="https://api.example.com",
                scope="collection",
                resource="record",
                query=(("page", 2),),
            )
        )

    assert siren(SCHEMA).project(
        SirenContext(base_url="https://api.example.com", scope="collection", resource="record", query=(("page", 2),))
    )["links"] == [{"rel": ["self"], "href": "https://api.example.com/records?page=2"}]
