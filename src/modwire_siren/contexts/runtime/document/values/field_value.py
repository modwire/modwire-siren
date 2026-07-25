from pydantic import StrictFloat, StrictInt

from modwire_siren.shared import BaseValue


class SirenFieldValue(BaseValue):
    """Describe a selectable Siren action field value."""

    value: str | StrictInt | StrictFloat
    title: str | None = None
    selected: bool = False
