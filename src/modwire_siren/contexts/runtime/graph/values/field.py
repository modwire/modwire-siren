from modwire_siren.contexts.shared import BaseValue, SirenFieldType


class SirenField(BaseValue):
    name: str
    type: SirenFieldType
