from dataclasses import dataclass


@dataclass(frozen=True)
class FieldDraft:
    operation: str
    name: str
    type: str
