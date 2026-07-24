import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


class TestSirenSpecCommand:
    def test_command_fails_after_a_public_schema_narrows_an_official_requirement(self, tmp_path: Path):
        workspace = self.workspace(tmp_path)
        field_value = workspace / "src/modwire_siren/runtime/document/values/field_value.py"
        field_value.write_text(field_value.read_text().replace("value: str | int | float", "value: str | int"))

        result = self.command(workspace)

        assert result.returncode != 0
        assert "✗ FieldValueObject.value — structural contract" in result.stdout
        assert "Siren conformance ledger has unimplemented structural requirements:" in result.stderr
        assert "FieldValueObject.value." in result.stderr

    def test_command_fails_for_an_unsupported_official_schema_term(self, tmp_path: Path):
        workspace = self.workspace(tmp_path)
        schema = workspace / "src/modwire_siren/runtime/document/schema/siren.schema.json"
        document = json.loads(schema.read_text())
        document["definitions"]["Action"]["properties"]["href"]["minLength"] = 1
        schema.write_text(json.dumps(document))

        result = self.command(workspace)

        assert result.returncode != 0
        assert "Unsupported Siren schema terms: minLength" in result.stderr

    def test_command_prints_the_unified_siren_conformance_ledger(self):
        result = self.command(Path(__file__).parents[1])

        assert result.returncode == 0, result.stderr
        assert "Siren conformance ledger" in result.stdout
        assert "  Structural contract" in result.stdout
        assert "  Executable specification" in result.stdout
        assert "      ✓ Action.method.PATCH — structural contract" in result.stdout
        assert "      ✓ EmbeddedLinkSubEntity.rel — structural contract" in result.stdout
        assert "      ✓ EmbeddedRepresentationSubEntity.rel — structural contract" in result.stdout
        assert "      ✓ Link.rel — structural contract" in result.stdout
        assert "      ✓ Action.href — structural contract" in result.stdout
        assert "      ✓ Action.type — structural contract" in result.stdout
        assert "      ✓ EmbeddedLinkSubEntity.href — structural contract" in result.stdout
        assert "      ✓ EmbeddedLinkSubEntity.type — structural contract" in result.stdout
        assert "      ✓ Link.href — structural contract" in result.stdout
        assert "      ✓ Link.type — structural contract" in result.stdout
        assert "      ✓ A root entity serializes a self link — executable specification" in result.stdout
        assert "      ✓ Duplicate action names are rejected — executable specification" in result.stdout
        assert "      ✓ Duplicate field names are rejected — executable specification" in result.stdout
        assert "      ✓ An action with fields serializes its default type — executable specification" in result.stdout
        assert "      ✓ A link with a non-URI href is rejected — executable specification" in result.stdout
        definitions = tuple(
            line[4:]
            for line in result.stdout.splitlines()
            if line.startswith("    ") and not line.startswith("      ")
        )

        assert definitions[:7] == (
            "Entity",
            "EmbeddedLinkSubEntity",
            "EmbeddedRepresentationSubEntity",
            "Action",
            "Field",
            "FieldValueObject",
            "Link",
        )

    def command(self, workspace: Path) -> subprocess.CompletedProcess[str]:
        python_path = os.pathsep.join((str(workspace / "src"), os.environ.get("PYTHONPATH", "")))
        return subprocess.run(
            ("make", "siren-spec"),
            cwd=workspace,
            capture_output=True,
            env={**os.environ, "PYTHON": sys.executable, "PYTHONPATH": python_path},
            text=True,
        )

    def workspace(self, tmp_path: Path) -> Path:
        project = Path(__file__).parents[1]
        workspace = tmp_path / "workspace"
        shutil.copytree(project / "src", workspace / "src")
        shutil.copytree(project / "tests/conformance", workspace / "tests/conformance")
        shutil.copytree(project / "scripts", workspace / "scripts")
        shutil.copy2(project / "Makefile", workspace / "Makefile")
        return workspace
