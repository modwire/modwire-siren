from dataclasses import dataclass


@dataclass(frozen=True)
class SirenExpectedScenario:
    feature: str
    name: str
