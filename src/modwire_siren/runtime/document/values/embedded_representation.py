from pydantic import Field

from .document import SirenDocument


class SirenEmbeddedRepresentation(SirenDocument):
    """Represent a Siren sub-entity embedded in full."""

    rel: tuple[str, ...] = Field(min_length=1)
