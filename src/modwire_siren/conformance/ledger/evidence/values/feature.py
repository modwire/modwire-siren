from dataclasses import dataclass

from .scenario import SirenBddScenario


@dataclass(frozen=True)
class SirenBddFeature:
    name: str
    scenarios: tuple[SirenBddScenario, ...]
