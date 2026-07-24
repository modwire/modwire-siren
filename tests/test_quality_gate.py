from pathlib import Path


class TestQualityGate:
    def test_ci_runs_the_complete_quality_gate_and_retains_package_evidence(self):
        project = Path(__file__).parents[1]
        workflow = (project / ".github/workflows/ci.yml").read_text()
        makefile = (project / "Makefile").read_text()

        assert "quality: modwire verify package-check" in makefile
        assert "rm -rf dist/quality" in makefile
        assert "$(RUN) -m build --wheel --sdist --outdir dist/quality" in makefile
        assert "$(RUN) -m twine check dist/quality/*" in makefile
        assert "- run: make quality" in workflow
        assert "python -m pip install -e \".[dev]\"" in workflow
        assert "setup-uv" not in workflow
        assert "if: always()" in workflow
        assert "path: dist/quality/" in workflow
