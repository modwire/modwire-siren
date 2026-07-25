from pydantic import StrictFloat, StrictInt

from modwire_siren.contexts.shared import BaseValue, SirenFieldType

from .field_value import SirenFieldValue


class SirenField(BaseValue):
    """Describe an official Siren action field."""

    name: str
    type: SirenFieldType = SirenFieldType.default()
    title: str | None = None
    value: str | StrictInt | StrictFloat | tuple[SirenFieldValue, ...] | None = None
