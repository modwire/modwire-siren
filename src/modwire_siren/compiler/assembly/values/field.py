from modwire_siren.shared import BaseValue, SirenFieldType


class FieldDraft(BaseValue):
    operation: str
    name: str
    type: SirenFieldType
