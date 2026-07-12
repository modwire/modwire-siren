import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).parents[1]
PROFILE_ROOT = ROOT / "docs" / "siren-ui-profile"
SCHEMA_PATH = PROFILE_ROOT / "schema" / "profile.schema.json"
VALID = PROFILE_ROOT / "examples" / "valid"
INVALID = PROFILE_ROOT / "examples" / "invalid"
NORMALIZED = PROFILE_ROOT / "examples" / "normalized"
PROFILE = "https://modwire.pmstag.online/profiles/siren-ui/v1"
PROFILE_REL = "https://modwire.pmstag.online/rels/ui-profile"


def read_json(path: Path):
    return json.loads(path.read_text())


def profile_metadata(document: dict) -> dict:
    candidates = [
        entity
        for entity in document["entities"]
        if PROFILE_REL in entity.get("rel", ())
    ]
    assert len(candidates) == 1
    return candidates[0]["properties"]


def test_profile_schema_is_valid_draft_2020_12():
    Draft202012Validator.check_schema(read_json(SCHEMA_PATH))


@pytest.mark.parametrize("path", sorted(VALID.glob("*.json")), ids=lambda path: path.stem)
def test_valid_complete_siren_examples_have_discovery_and_valid_metadata(path: Path):
    document = read_json(path)
    profile_links = [link for link in document["links"] if "profile" in link["rel"]]

    assert profile_links == [{"rel": ["profile"], "href": PROFILE}]
    Draft202012Validator(read_json(SCHEMA_PATH)).validate(profile_metadata(document))


@pytest.mark.parametrize("path", sorted(INVALID.glob("*.json")), ids=lambda path: path.stem)
def test_invalid_metadata_examples_are_rejected(path: Path):
    with pytest.raises(ValidationError):
        Draft202012Validator(read_json(SCHEMA_PATH)).validate(read_json(path))


def test_normalized_fixtures_are_json_and_reference_a_valid_example():
    normalized = read_json(NORMALIZED / "entity-detail.json")
    source = read_json(VALID / "entity-detail.json")

    assert normalized["role"] == profile_metadata(source)["presentation"]["role"]
    assert normalized["classes"] == source["class"]
    assert normalized["diagnostics"] == []


def test_owner_approval_is_recorded_before_implementation():
    checklist = (PROFILE_ROOT / "review-checklist.md").read_text()

    assert "Decision: `approved`" in checklist
    assert "Decision: `pending`" not in checklist
    assert "Status: **Approved — implementation authorized**" in (
        PROFILE_ROOT / "README.md"
    ).read_text()
