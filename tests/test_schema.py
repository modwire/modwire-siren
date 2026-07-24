import json
from importlib.resources import files

import pytest
from jsonschema import Draft4Validator, FormatChecker, ValidationError

import modwire_siren
from modwire_siren import (
    SirenAction,
    SirenDocument,
    SirenEmbeddedLink,
    SirenEmbeddedRepresentation,
    SirenField,
    SirenLink,
)


class TestSchema:
    schema = json.loads(files(modwire_siren).joinpath("runtime/document/schema/siren.schema.json").read_text())
    validator = Draft4Validator(schema, format_checker=FormatChecker())

    @pytest.mark.parametrize(
        "payload",
        [
            {"links": [{"rel": ["self"], "href": "https://[invalid"}]},
            {"entities": [{"rel": []}]},
            {
                "actions": [
                    {
                        "name": "rename",
                        "href": "https://api.example.com/records/42",
                        "fields": [{"name": "title", "type": "unsupported"}],
                    }
                ]
            },
        ],
    )
    def test_pinned_schema_rejects_invalid_public_payloads(self, payload):
        with pytest.raises(ValidationError):
            self.validator.validate(payload)

    def test_public_models_reject_package_specific_action_field_members(self):
        with pytest.raises(ValueError, match="Extra inputs are not permitted"):
            SirenField(name="title", required=True)

    def test_pinned_schema_identifies_the_upstream_draft_four_revision(self):
        assert self.schema["id"] == "http://sirenspec.org/schema#"
        assert self.schema["$schema"] == "http://json-schema.org/draft-04/schema#"
        assert "uri" in FormatChecker().checkers

    def test_public_root_fixture_conforms_to_the_pinned_schema(self):
        document = SirenDocument(
            class_=("api", "entry-point"),
            actions=(SirenAction(name="search", method="POST", href="https://api.example.com/search"),),
            links=(SirenLink(rel=("self",), href="https://api.example.com/"),),
        )

        self.validator.validate(document.model_dump(by_alias=True, mode="json", exclude_none=True))

    def test_public_collection_fixture_conforms_to_the_pinned_schema(self):
        document = SirenDocument(
            class_=("collection",),
            properties={"count": 1},
            entities=(
                SirenEmbeddedRepresentation(
                    class_=("record",),
                    rel=("item",),
                    properties={"id": "42"},
                    links=(SirenLink(rel=("self",), href="https://api.example.com/records/42"),),
                ),
            ),
            actions=(SirenAction(name="list", href="https://api.example.com/records"),),
            links=(SirenLink(rel=("self",), href="https://api.example.com/records"),),
        )

        self.validator.validate(document.model_dump(by_alias=True, mode="json", exclude_none=True))

    def test_public_entity_and_embedded_link_fixtures_conform_to_the_pinned_schema(self):
        document = SirenDocument(
            class_=("record",),
            properties={"id": "42"},
            entities=(
                SirenEmbeddedLink(
                    rel=("collection",),
                    href="https://api.example.com/records",
                ),
            ),
            actions=(
                SirenAction(
                    name="rename",
                    method="PATCH",
                    href="https://api.example.com/records/42",
                    type="application/json",
                    fields=(SirenField(name="title", type="text"),),
                ),
            ),
            links=(SirenLink(rel=("self",), href="https://api.example.com/records/42"),),
        )

        self.validator.validate(document.model_dump(by_alias=True, mode="json", exclude_none=True))
