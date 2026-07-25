from modwire_siren.shared import BaseValue

from .scenario import SirenBddScenario


class SirenBddFeature(BaseValue):
    name: str
    scenarios: tuple[SirenBddScenario, ...]
