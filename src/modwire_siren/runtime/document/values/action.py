from pydantic import Field

from ...contracts import Contract
from ...vocabulary import SirenActionMethod
from .field import SirenField


class SirenAction(Contract):
    """Describe an available Siren action."""

    class_: tuple[str, ...] | None = Field(default=None, alias="class")
    name: str
    method: SirenActionMethod = SirenActionMethod.GET
    href: str
    title: str | None = None
    type: str | None = None
    fields: tuple[SirenField, ...] | None = None
