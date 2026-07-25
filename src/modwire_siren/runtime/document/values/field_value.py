from pydantic import StrictFloat, StrictInt

from ...contracts import Contract


class SirenFieldValue(Contract):
    """Describe a selectable Siren action field value."""

    value: str | StrictInt | StrictFloat
    title: str | None = None
    selected: bool = False
