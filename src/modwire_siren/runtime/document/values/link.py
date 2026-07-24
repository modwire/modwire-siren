from pydantic import Field

from ...contracts import Contract


class SirenLink(Contract):
    """Describe a navigational Siren link."""

    class_: tuple[str, ...] = Field(default=(), alias="class")
    title: str | None = None
    rel: tuple[str, ...] = Field(min_length=1)
    href: str
    type: str | None = None
