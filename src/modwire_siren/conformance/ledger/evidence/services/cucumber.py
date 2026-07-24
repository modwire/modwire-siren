import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from wireup import injectable

from ..contracts import SirenBddEvidenceReader
from ..values import SirenBddFeature, SirenBddScenario


@injectable(as_type=SirenBddEvidenceReader)
@dataclass(frozen=True)
class SirenCucumberEvidenceReader(SirenBddEvidenceReader):
    def read(self, cucumber_report: Path) -> tuple[SirenBddFeature, ...]:
        document = json.loads(cucumber_report.read_text())
        if not isinstance(document, list):
            raise ValueError("Cucumber report must contain a feature list.")
        expected_failures = self.expected_failures(cucumber_report.with_name("junit.xml"))
        features = tuple(self.feature(value, expected_failures) for value in document)
        identifiers = {scenario.identifier for feature in features for scenario in feature.scenarios}
        unreported = expected_failures.difference(identifiers)
        if unreported:
            names = ", ".join(sorted(unreported))
            raise ValueError(f"JUnit report has no matching Cucumber scenarios: {names}.")
        return features

    def feature(self, value: Any, expected_failures: frozenset[str]) -> SirenBddFeature:
        if not isinstance(value, Mapping):
            raise ValueError("Cucumber report feature must be an object.")
        name = value.get("name")
        scenarios = value.get("elements")
        if not isinstance(name, str) or not name:
            raise ValueError("Cucumber report feature must have a name.")
        if not isinstance(scenarios, list):
            raise ValueError(f"Cucumber report feature {name!r} must contain scenarios.")
        return SirenBddFeature(name, tuple(self.scenario(value, expected_failures) for value in scenarios))

    def scenario(self, value: Any, expected_failures: frozenset[str]) -> SirenBddScenario:
        if not isinstance(value, Mapping):
            raise ValueError("Cucumber report scenario must be an object.")
        identifier = value.get("id")
        name = value.get("name")
        steps = value.get("steps")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError("Cucumber report scenario must have an identifier.")
        if not isinstance(name, str) or not name:
            raise ValueError("Cucumber report scenario must have a name.")
        if not isinstance(steps, list) or not steps:
            raise ValueError(f"Cucumber report scenario {name!r} must contain steps.")
        statuses = tuple(self.status(value, name) for value in steps)
        if all(status == "passed" for status in statuses):
            if identifier in expected_failures:
                raise ValueError(f"Cucumber report scenario {name!r} unexpectedly passed.")
            return SirenBddScenario(identifier, name, True)
        if identifier in expected_failures and statuses[-1] == "skipped" and all(
            status == "passed" for status in statuses[:-1]
        ):
            return SirenBddScenario(identifier, name, False)
        detail = ", ".join(statuses)
        raise ValueError(f"Cucumber report scenario {name!r} has unexpected results: {detail}.")

    def expected_failures(self, junit_report: Path) -> frozenset[str]:
        document = ElementTree.parse(junit_report)
        names: set[str] = set()
        for testcase in document.findall(".//testcase"):
            name = testcase.get("name")
            skipped = testcase.find("skipped")
            if skipped is None:
                continue
            if not name or skipped.get("type") != "pytest.xfail":
                raise ValueError("JUnit report contains a skipped test that is not a strict expected failure.")
            if name in names:
                raise ValueError(f"JUnit report has duplicate expected failure names: {name}.")
            names.add(name)
        return frozenset(names)

    def status(self, value: Any, scenario: str) -> str:
        if not isinstance(value, Mapping):
            raise ValueError(f"Cucumber report scenario {scenario!r} has an invalid step.")
        result = value.get("result")
        if not isinstance(result, Mapping) or not isinstance(result.get("status"), str):
            raise ValueError(f"Cucumber report scenario {scenario!r} has an invalid step result.")
        return result["status"]
