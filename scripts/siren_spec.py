import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from sirenity.wiring import SirenApplicationContainer

with TemporaryDirectory() as directory:
    cucumber_report = Path(directory) / "cucumber.json"
    result = subprocess.run(
        (
            sys.executable,
            "-m",
            "pytest",
            "tests/conformance",
            "--cucumberjson",
            str(cucumber_report),
            "--junitxml",
            str(cucumber_report.with_name("junit.xml")),
            "-q",
        ),
        capture_output=True,
        text=True,
    )
    if result.returncode:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    conformance = SirenApplicationContainer().application().conformance_service()
    report = conformance.inspect(cucumber_report, Path("tests/conformance/features"))
    print(conformance.render(report))
    conformance.verify(report)
