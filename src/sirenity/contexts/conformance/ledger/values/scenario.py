from sirenity.contexts.shared import BaseValue


class SirenBddScenario(BaseValue):
    identifier: str
    name: str
    implemented: bool
