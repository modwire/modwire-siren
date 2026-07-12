import json
from pathlib import Path

import pytest

from modwire_siren import ModwireSirenFactory, SirenEntityRequest
from modwire_siren.error import SirenError
from modwire_siren.profile import SirenProfile

ROOT = Path(__file__).parents[1]
PROFILE_ROOT = ROOT / "docs" / "siren-ui-profile"
VALID = PROFILE_ROOT / "examples" / "valid"
INVALID = PROFILE_ROOT / "examples" / "invalid"
PROFILE = SirenProfile()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def contains_null(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, dict):
        return any(contains_null(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_null(item) for item in value)
    return False


@pytest.mark.parametrize("path", sorted(VALID.glob("*.json")), ids=lambda path: path.stem)
def test_profile_discovers_every_approved_document_with_progressive_defaults(path: Path):
    document = read_json(path)

    metadata = PROFILE.discover(document)

    assert metadata["profile"] == PROFILE.identifier
    assert metadata["presentation"]["layout"]["kind"]
    assert {"profile", "presentation", "properties", "relations", "actions", "extensions"} <= set(metadata)
    assert not contains_null(metadata)


@pytest.mark.parametrize("path", sorted(INVALID.glob("*.json")), ids=lambda path: path.stem)
def test_profile_rejects_every_approved_negative_fixture(path: Path):
    with pytest.raises(SirenError) as raised:
        PROFILE.validate(read_json(path))

    assert raised.value.kind == "profile.invalid"
    assert raised.value.issues


def test_profile_defaults_are_complete_without_serializing_nulls():
    metadata = PROFILE.validate(
        {"profile": PROFILE.identifier, "presentation": {"role": "detail"}}
    )

    assert metadata == {
        "profile": PROFILE.identifier,
        "presentation": {"role": "detail", "layout": {"kind": "flow", "regions": []}},
        "properties": {},
        "relations": {},
        "actions": {},
        "extensions": {},
    }
    assert not contains_null(metadata)


def test_profile_defaults_progressively_complete_nested_metadata():
    metadata = PROFILE.validate(
        {
            "profile": PROFILE.identifier,
            "presentation": {"role": "detail"},
            "properties": {"title": {}},
            "relations": {"section": {"role": "supplementary"}},
            "actions": {"revise": {"fields": {"title": {}}}},
        }
    )

    assert metadata["properties"]["title"] == {
        "order": 0,
        "format": "text",
        "importance": "supporting",
        "sensitive": False,
    }
    assert metadata["relations"]["section"] == {
        "role": "supplementary",
        "loading": "manual",
        "cardinality": "one",
        "order": 0,
    }
    assert metadata["actions"]["revise"] == {
        "intent": "secondary",
        "placement": "entity",
        "order": 0,
        "fields": {"title": {"widget": "automatic", "order": 0}},
        "result": {"mode": "none", "relations": [], "optimistic": False},
    }


@pytest.mark.parametrize(
    "metadata",
    [
        {"profile": None, "presentation": {"role": "detail"}},
        {"profile": "", "presentation": {"role": "detail"}},
        {"profile": PROFILE.identifier, "presentation": {"role": "detail", "layout": None}},
        {"profile": PROFILE.identifier, "presentation": {"role": "detail", "label": None}},
    ],
)
def test_profile_rejects_null_and_empty_contract_values(metadata: dict):
    with pytest.raises(SirenError, match="JSON Schema"):
        PROFILE.validate(metadata)


def test_profile_schema_identity_and_media_type_come_from_the_packaged_schema():
    assert PROFILE.schema_id == (
        "https://raw.githubusercontent.com/modwire/modwire-siren/main/"
        "docs/siren-ui-profile/schema/profile.schema.json"
    )
    assert PROFILE.media_type == f'application/vnd.siren+json; profile="{PROFILE.identifier}"'


def test_profile_discovery_uses_one_siren_error_contract():
    document = {"class": ["record"], "properties": {}, "entities": [], "actions": [], "links": []}

    with pytest.raises(SirenError) as raised:
        PROFILE.discover(document)

    assert raised.value.as_dict() == {
        "kind": "profile.discovery",
        "detail": "A profiled Siren document requires exactly one profile link and profile entity",
        "issues": [],
    }


def test_profile_reports_dangling_references_with_json_pointer():
    document = read_json(VALID / "entity-detail.json")
    profile = next(
        entity["properties"]
        for entity in document["entities"]
        if entity.get("class") == ["modwire-ui-profile"]
    )
    profile["properties"]["missing"] = {"label": "Missing"}

    with pytest.raises(SirenError) as raised:
        PROFILE.discover(document)

    assert raised.value.kind == "profile.invalid"
    assert raised.value.issues == (
        {
            "pointer": "/properties/missing",
            "message": "Profile references unknown Siren property: 'missing'",
        },
    )


def test_profile_enhances_a_manually_assembled_siren_dictionary():
    document = {
        "class": ["record"],
        "properties": {"slug": "architecture", "title": "Architecture"},
        "entities": [{"class": ["section"], "rel": ["section"], "properties": {"title": "Contracts"}}],
        "actions": [{"name": "revise", "href": "/records/architecture", "method": "PATCH", "fields": []}],
        "links": [{"rel": ["self"], "href": "/records/architecture"}],
    }
    original = json.loads(json.dumps(document))
    metadata = {
        "profile": PROFILE.identifier,
        "presentation": {"role": "detail"},
        "properties": {"title": {"importance": "primary"}},
        "relations": {"section": {"role": "supplementary"}},
        "actions": {"revise": {"intent": "primary"}},
    }

    enhanced = PROFILE.enhance(document, metadata)

    assert document == original
    assert PROFILE.discover(enhanced)["actions"]["revise"]["intent"] == "primary"
    assert enhanced["links"][-1] == {"rel": ["profile"], "href": PROFILE.identifier}
    assert enhanced["entities"][-1]["class"] == ["modwire-ui-profile"]


def test_openapi_and_manual_documents_share_the_same_profile_contract():
    metadata = {
        "profile": PROFILE.identifier,
        "presentation": {
            "role": "detail",
            "layout": {
                "kind": "flow",
                "regions": [
                    {
                        "id": "commands",
                        "content": {"properties": ["title"], "actions": ["publish", "archive"]},
                    }
                ],
            },
        },
        "properties": {"title": {"label": "Title", "importance": "primary"}},
        "actions": {
            "publish": {"intent": "primary"},
            "archive": {"intent": "destructive", "confirmation": {"required": True}},
        },
    }
    schema = {
        "paths": {
            "/articles/{article_id}": {
                "x-siren-resource": {
                    "name": "article",
                    "class": "article",
                    "identifier": "id",
                    "path-parameters": {"article_id": "id"},
                    "relations": {},
                },
                "x-siren-ui-profile": metadata,
                "get": {"operationId": "get_article"},
                "post": {"operationId": "publish"},
                "delete": {"operationId": "archive"},
            }
        }
    }
    siren = ModwireSirenFactory.standard(schema, "https://api.test")

    document = siren.document(
        SirenEntityRequest(
            resource_name="article",
            properties={"id": "draft", "title": "Profile draft"},
            operation_ids=("publish",),
            path_values={},
            entities=(),
        )
    )
    projected = PROFILE.discover(document)

    assert [action["name"] for action in document["actions"]] == ["publish"]
    assert set(projected["actions"]) == {"publish"}
    assert projected["presentation"]["layout"]["regions"][0]["content"]["actions"] == ["publish"]


def test_profile_schema_runtime_asset_cannot_drift_from_normative_document():
    packaged = ROOT / "src" / "modwire_siren" / "profile" / "schema" / "profile.schema.json"
    normative = PROFILE_ROOT / "schema" / "profile.schema.json"

    assert packaged.read_bytes() == normative.read_bytes()
