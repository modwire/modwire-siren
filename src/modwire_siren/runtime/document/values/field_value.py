from ...contracts import Contract


class SirenFieldValue(Contract):
    """Describe a selectable Siren action field value."""

    value: str | int | float
    title: str | None = None
    selected: bool = False
