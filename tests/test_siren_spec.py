import subprocess
from pathlib import Path


class TestSirenSpecCommand:
    def test_command_prints_the_structural_siren_contract(self):
        result = subprocess.run(("make", "siren-spec"), cwd=Path(__file__).parents[1], capture_output=True, text=True)

        assert result.returncode == 0, result.stderr
        assert "Siren structural contract" in result.stdout
        assert "Entity.class" in result.stdout
        assert "Action.method.PATCH" in result.stdout
        assert "✗ EmbeddedLinkSubEntity.rel" in result.stdout
        assert "✗ EmbeddedLinkSubEntity.type" in result.stdout
        assert "✗ Link.rel" in result.stdout
        assert "✗ Link.type" in result.stdout
        assert "✓ Field.value" in result.stdout
        labels = tuple(
            line.split(" — ", maxsplit=1)[0][2:]
            for line in result.stdout.splitlines()
            if line.startswith(("✓ ", "✗ "))
        )
        definitions = tuple(dict.fromkeys(label.split(".", maxsplit=1)[0] for label in labels))

        assert definitions == (
            "Entity",
            "EmbeddedLinkSubEntity",
            "EmbeddedRepresentationSubEntity",
            "Action",
            "Field",
            "FieldValueObject",
            "Link",
        )
