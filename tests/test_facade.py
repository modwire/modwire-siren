from copy import deepcopy
from inspect import Parameter, signature
from pathlib import Path

import pytest
from openapi_documents import SCHEMA

import modwire_siren
from modwire_siren import (
    ModwireSirenError,
    SirenAction,
    SirenCompatibilityFinding,
    SirenCompatibilityReport,
    SirenContext,
    SirenDocument,
    SirenEmbeddedLink,
    SirenEmbeddedRepresentation,
    SirenField,
    SirenFieldValue,
    SirenLink,
    SirenRelationship,
    audit,
    siren,
)


class TestFacade:
    @pytest.mark.parametrize(
        ("openapi", "source_path", "public_path"),
        [
            ([], "/", "/"),
            (SCHEMA, "service", "/"),
            (SCHEMA, "/", "siren"),
        ],
    )
    def test_public_facade_rejects_invalid_inputs_before_the_happy_path(
        self, openapi, source_path, public_path
    ):
        with pytest.raises(ModwireSirenError, match="Invalid or unsupported OpenAPI contract"):
            siren(openapi, source_path=source_path, public_path=public_path)

    def test_public_facade_exports_siren_contracts_and_composition_entry_points(self):
        assert modwire_siren.__all__ == [
            "ModwireSirenError",
            "SirenAction",
            "SirenCompatibilityFinding",
            "SirenCompatibilityReport",
            "SirenContext",
            "SirenDocument",
            "SirenEmbeddedLink",
            "SirenEmbeddedRepresentation",
            "SirenField",
            "SirenFieldValue",
            "SirenLink",
            "SirenRelationship",
            "audit",
            "siren",
        ]
        assert (
            ModwireSirenError,
            SirenAction,
            SirenCompatibilityFinding,
            SirenCompatibilityReport,
            SirenDocument,
            SirenEmbeddedLink,
            SirenEmbeddedRepresentation,
            SirenField,
            SirenFieldValue,
            SirenLink,
            SirenRelationship,
            audit,
        ) == (
            modwire_siren.ModwireSirenError,
            modwire_siren.SirenAction,
            modwire_siren.SirenCompatibilityFinding,
            modwire_siren.SirenCompatibilityReport,
            modwire_siren.SirenDocument,
            modwire_siren.SirenEmbeddedLink,
            modwire_siren.SirenEmbeddedRepresentation,
            modwire_siren.SirenField,
            modwire_siren.SirenFieldValue,
            modwire_siren.SirenLink,
            modwire_siren.SirenRelationship,
            modwire_siren.audit,
        )
        parameters = signature(siren).parameters
        assert tuple(parameters) == ("openapi", "source_path", "public_path")
        assert parameters["openapi"].kind is Parameter.POSITIONAL_OR_KEYWORD
        assert parameters["source_path"].kind is Parameter.KEYWORD_ONLY
        assert parameters["source_path"].default == "/"
        assert parameters["public_path"].kind is Parameter.KEYWORD_ONLY
        assert parameters["public_path"].default == "/"
        assert tuple(signature(audit).parameters) == ("openapi",)


    def test_public_facade_remounts_source_paths_without_mutating_the_openapi_document(self):
        schema = deepcopy(SCHEMA)
        schema["paths"] = {f"/service{path}": item for path, item in schema["paths"].items()}
        original = deepcopy(schema)

        document = siren(schema, source_path="/service/", public_path="/siren/").project(
            SirenContext(base_url="https://api.example.com", scope="root")
        )

        assert document.model_dump(by_alias=True, mode="json", exclude_none=True)["links"] == [
            {"rel": ["self"], "href": "https://api.example.com/siren"},
            {"rel": ["collection"], "href": "https://api.example.com/siren/records"},
        ]
        assert schema == original

    def test_public_facade_rejects_paths_outside_the_segment_aware_source_prefix(self):
        schema = deepcopy(SCHEMA)
        schema["paths"] = {f"/services{path}": item for path, item in schema["paths"].items()}

        with pytest.raises(ModwireSirenError, match="Invalid or unsupported OpenAPI contract"):
            siren(schema, source_path="/service", public_path="/siren")

    def test_generated_public_api_hides_framework_validator_hooks(self):
        documentation = (Path(__file__).parents[1] / "README.md").read_text()

        assert "apply_default_media_type()" not in documentation
        assert "validate_field_names()" not in documentation
        assert "validate_scope()" not in documentation
        assert "validate_action_names()" not in documentation
        assert "| `SirenAction` | Describe an available Siren action. | — |" in documentation
