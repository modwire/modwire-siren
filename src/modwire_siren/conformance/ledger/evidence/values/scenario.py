from dataclasses import dataclass


@dataclass(frozen=True)
class SirenBddScenario:
    identifier: str
    name: str
    implemented: bool
