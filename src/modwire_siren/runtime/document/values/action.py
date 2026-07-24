from pydantic import Field

from ...contracts import Contract
from ...vocabulary import SirenActionMethod, SirenMediaType, SirenUri
from .field import SirenField


class SirenAction(Contract):
    """Describe an available Siren action."""

    class_: tuple[str, ...] | None = Field(default=None, alias="class")
    name: str
    method: SirenActionMethod = SirenActionMethod.GET
    href: SirenUri
    title: str | None = None
    type: SirenMediaType | None = None
    fields: tuple[SirenField, ...] | None = None
