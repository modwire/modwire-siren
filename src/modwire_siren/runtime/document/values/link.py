from pydantic import Field

from ...contracts import Contract
from ...vocabulary import SirenRelation


class SirenLink(Contract):
    """Describe a navigational Siren link."""

    class_: tuple[str, ...] | None = Field(default=None, alias="class")
    title: str | None = None
    rel: tuple[SirenRelation, ...] = Field(min_length=1)
    href: str
    type: str | None = None
