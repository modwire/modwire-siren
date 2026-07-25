from modwire_siren.contexts.shared import BaseValue, SirenFieldType


class FieldDraft(BaseValue):
    operation: str
    name: str
    type: SirenFieldType
    values: tuple[str | int | float, ...] = ()
