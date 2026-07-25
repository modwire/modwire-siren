from modwire_siren.contexts.shared import BaseValue, SirenFieldType


class Field(BaseValue):
    name: str
    type: SirenFieldType
