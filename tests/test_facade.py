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
    audit,
    siren,
)


class TestFacade:
    @pytest.mark.parametrize(
        ("openapi", "root_path"),
        [
            ([], "/"),
            (SCHEMA, "siren"),
        ],
    )
    def test_public_facade_rejects_invalid_inputs_before_the_happy_path(self, openapi, root_path):
        with pytest.raises(ModwireSirenError, match="Invalid or unsupported OpenAPI contract"):
            siren(openapi, root_path=root_path)

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
            modwire_siren.audit,
        )
        parameters = signature(siren).parameters
        assert tuple(parameters) == ("openapi", "root_path")
        assert parameters["openapi"].kind is Parameter.POSITIONAL_OR_KEYWORD
        assert parameters["root_path"].kind is Parameter.KEYWORD_ONLY
        assert parameters["root_path"].default == "/"
        assert tuple(signature(audit).parameters) == ("openapi",)


    def test_public_facade_uses_an_explicit_mounted_root_path(self):
        document = siren(SCHEMA, root_path="/siren/").project(
            SirenContext(base_url="https://api.example.com", scope="root")
        )

        assert document.model_dump(by_alias=True, mode="json", exclude_none=True)["links"][0] == {
            "rel": ["self"],
            "href": "https://api.example.com/siren/",
        }

    def test_generated_public_api_hides_framework_validator_hooks(self):
        documentation = (Path(__file__).parents[1] / "README.md").read_text()

        assert "apply_default_media_type()" not in documentation
        assert "validate_field_names()" not in documentation
        assert "validate_scope()" not in documentation
        assert "validate_action_names()" not in documentation
        assert "| `SirenAction` | Describe an available Siren action. | — |" in documentation
