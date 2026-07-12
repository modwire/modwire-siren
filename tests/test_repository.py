import json
import runpy
from importlib.resources import files
from pathlib import Path

from modwire_siren import SirenClient

ROOT = Path(__file__).parents[1]


def test_profile_schema_is_a_runtime_package_resource():
    schema = json.loads(
        files("modwire_siren.profile")
        .joinpath("schema/profile.schema.json")
        .read_text(encoding="utf-8")
    )

    assert schema["$id"] == (
        "https://raw.githubusercontent.com/modwire/modwire-siren/main/"
        "docs/siren-ui-profile/schema/profile.schema.json"
    )


def test_documented_example_executes():
    namespace = runpy.run_path(ROOT / "examples/build_document.py")
    assert namespace["document"]["class"] == ["record"]

    profile = runpy.run_path(ROOT / "examples/profile.py")
    assert profile["document"]["entities"][-1]["class"] == ["modwire-ui-profile"]


def test_generated_signatures_are_stable_for_postponed_annotations():
    generator = runpy.run_path(ROOT / "scripts/generate_docs.py")[
        "DocumentationGenerator"
    ]

    operations = generator._operations(SirenClient)

    assert "payload: Mapping[str, Any] | None = None" in operations
    assert "'Mapping[str, Any]" not in operations


def test_release_uses_trusted_publishing_without_secrets():
    source = (ROOT / ".github/workflows/release.yml").read_text()
    publish = source.split("  publish-pypi:", 1)[1].split("  github-release:", 1)[0]
    assert "environment:\n      name: pypi" in publish
    assert "permissions:\n      id-token: write" in publish
    assert "pypa/gh-action-pypi-publish@release/v1" in publish
    assert "password:" not in publish and "secrets." not in publish
