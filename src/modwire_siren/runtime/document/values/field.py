from ...contracts import Contract
from ...vocabulary import SirenFieldType
from .field_value import SirenFieldValue


class SirenField(Contract):
    """Describe an official Siren action field."""

    name: str
    type: SirenFieldType = SirenFieldType.TEXT
    title: str | None = None
    value: str | int | float | tuple[SirenFieldValue, ...] | None = None
