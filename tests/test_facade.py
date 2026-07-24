from inspect import Parameter, signature

import pytest
from openapi_documents import SCHEMA

import modwire_siren
from modwire_siren import (
    SirenAction,
    SirenContext,
    SirenDocument,
    SirenEmbeddedLink,
    SirenEmbeddedRepresentation,
    SirenField,
    SirenFieldValue,
    SirenLink,
    siren,
)


def test_public_facade_exports_siren_contracts_and_composition_entry_points():
    assert modwire_siren.__all__ == [
        "SirenAction",
        "SirenContext",
        "SirenDocument",
        "SirenEmbeddedLink",
        "SirenEmbeddedRepresentation",
        "SirenField",
        "SirenFieldValue",
        "SirenLink",
        "siren",
    ]
    assert (
        SirenAction,
        SirenDocument,
        SirenEmbeddedLink,
        SirenEmbeddedRepresentation,
        SirenField,
        SirenFieldValue,
        SirenLink,
    ) == (
        modwire_siren.SirenAction,
        modwire_siren.SirenDocument,
        modwire_siren.SirenEmbeddedLink,
        modwire_siren.SirenEmbeddedRepresentation,
        modwire_siren.SirenField,
        modwire_siren.SirenFieldValue,
        modwire_siren.SirenLink,
    )
    parameters = signature(siren).parameters
    assert tuple(parameters) == ("openapi", "root_path")
    assert parameters["openapi"].kind is Parameter.POSITIONAL_OR_KEYWORD
    assert parameters["root_path"].kind is Parameter.KEYWORD_ONLY
    assert parameters["root_path"].default == "/"


def test_public_facade_uses_an_explicit_mounted_root_path():
    document = siren(SCHEMA, root_path="/siren/").project(
        SirenContext(base_url="https://api.example.com", scope="root")
    )

    assert document["links"][0] == {"rel": ["self"], "href": "https://api.example.com/siren/"}


@pytest.mark.parametrize(
    ("openapi", "root_path", "error", "message"),
    [
        ([], "/", TypeError, "OpenAPI document must be a mapping"),
        (SCHEMA, "siren", ValueError, "Siren root path must start"),
    ],
)
def test_public_facade_rejects_invalid_inputs_before_the_happy_path(openapi, root_path, error, message):
    with pytest.raises(error, match=message):
        siren(openapi, root_path=root_path)
