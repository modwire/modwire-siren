from pydantic import Field

from modwire_siren.shared import BaseValue, SirenMediaType, SirenRelation, SirenUri


class SirenLink(BaseValue):
    """Describe a navigational Siren link."""

    class_: tuple[str, ...] | None = Field(default=None, alias="class")
    title: str | None = None
    rel: tuple[SirenRelation, ...] = Field(min_length=1)
    href: SirenUri
    type: SirenMediaType | None = None
