from pydantic import StrictFloat, StrictInt

from sirenity.contexts.shared import BaseValue


class SirenFieldValue(BaseValue):
    """Describe a selectable Siren action field value."""

    value: str | StrictInt | StrictFloat
    title: str | None = None
    selected: bool = False
