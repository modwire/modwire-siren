import runpy
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_documented_example_executes():
    namespace = runpy.run_path(ROOT / "examples/build_document.py")
    assert namespace["document"]["class"] == ["record"]


def test_release_uses_trusted_publishing_without_secrets():
    source = (ROOT / ".github/workflows/release.yml").read_text()
    publish = source.split("  publish-pypi:", 1)[1].split("  github-release:", 1)[0]
    assert "environment:\n      name: pypi" in publish
    assert "permissions:\n      id-token: write" in publish
    assert "pypa/gh-action-pypi-publish@release/v1" in publish
    assert "password:" not in publish and "secrets." not in publish
