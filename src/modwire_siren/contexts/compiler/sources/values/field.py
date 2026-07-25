from modwire_siren.contexts.shared import BaseValue, SirenFieldType


class Field(BaseValue):
    name: str
    type: SirenFieldType
    values: tuple[str | int | float, ...] = ()
