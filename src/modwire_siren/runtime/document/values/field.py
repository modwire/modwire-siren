from pydantic import StrictFloat, StrictInt

from ....vocabulary import SirenFieldType
from ...contracts import Contract
from .field_value import SirenFieldValue


class SirenField(Contract):
    """Describe an official Siren action field."""

    name: str
    type: SirenFieldType = SirenFieldType.default()
    title: str | None = None
    value: str | StrictInt | StrictFloat | tuple[SirenFieldValue, ...] | None = None
