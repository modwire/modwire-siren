import subprocess
import sys
from pathlib import Path

from fastapi_fixture import FastApiOpenApiFixture

from modwire_siren import SirenContext, siren


def test_public_facade_compiles_a_framework_generated_openapi_document():
    document = siren(FastApiOpenApiFixture().document()).project(
        SirenContext(
            base_url="https://api.example.com",
            scope="collection",
            resource="widget",
            capabilities=frozenset({"list_widgets_api_v1_widgets_get"}),
        )
    )

    assert document["links"] == [{"rel": ["self"], "href": "https://api.example.com/api/v1/widgets"}]
    assert document["actions"] == [
        {
            "name": "list_widgets_api_v1_widgets_get",
            "href": "https://api.example.com/api/v1/widgets",
            "method": "GET",
        }
    ]


def test_built_wheel_supports_the_documented_public_consumer_flow(tmp_path: Path):
    project = Path(__file__).parents[1]
    artifacts = tmp_path / "artifacts"
    environment = tmp_path / "consumer"
    fixture = project / "tests" / "fixtures" / "wheel_consumer.py"
    subprocess.run(
        (sys.executable, "-m", "build", "--wheel", "--outdir", str(artifacts)),
        cwd=project,
        check=True,
        capture_output=True,
        text=True,
    )
    wheel = next(artifacts.glob("*.whl"))
    subprocess.run(
        (sys.executable, "-m", "venv", "--system-site-packages", str(environment)),
        check=True,
        capture_output=True,
        text=True,
    )
    consumer = environment / "bin" / "python"
    subprocess.run(
        (str(consumer), "-m", "pip", "install", str(wheel)),
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    result = subprocess.run(
        (str(consumer), str(fixture)),
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "site-packages/modwire_siren" in result.stdout
