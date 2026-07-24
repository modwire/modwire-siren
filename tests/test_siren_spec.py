import subprocess
from pathlib import Path


class TestSirenSpecCommand:
    def test_command_prints_the_structural_siren_contract(self):
        result = subprocess.run(("make", "siren-spec"), cwd=Path(__file__).parents[1], capture_output=True, text=True)

        assert result.returncode == 0, result.stderr
        assert "Siren structural contract" in result.stdout
        assert "Entity.class" in result.stdout
        assert "Action.method.PATCH" in result.stdout
