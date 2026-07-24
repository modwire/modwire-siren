import os
import subprocess
import sys
from pathlib import Path


class TestSirenSpecCommand:
    def test_command_prints_the_unified_siren_conformance_ledger(self):
        result = subprocess.run(
            ("make", "siren-spec"),
            cwd=Path(__file__).parents[1],
            capture_output=True,
            env={**os.environ, "PYTHON": sys.executable},
            text=True,
        )

        assert result.returncode == 0, result.stderr
        assert "Siren conformance ledger" in result.stdout
        assert "  Structural contract" in result.stdout
        assert "  Executable specification" in result.stdout
        assert "      ✓ Action.method.PATCH — structural contract" in result.stdout
        assert "      ✓ EmbeddedLinkSubEntity.rel — structural contract" in result.stdout
        assert "      ✓ EmbeddedRepresentationSubEntity.rel — structural contract" in result.stdout
        assert "      ✓ Link.rel — structural contract" in result.stdout
        assert "      ✓ Action.href — structural contract" in result.stdout
        assert "      ✓ EmbeddedLinkSubEntity.href — structural contract" in result.stdout
        assert "      ✓ Link.href — structural contract" in result.stdout
        assert "      ✓ A root entity serializes a self link — executable specification" in result.stdout
        assert "      ✗ Duplicate action names are rejected — expected failure" in result.stdout
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
