from typing import Annotated

from pydantic import Field

from .base import SirenContract


class SirenLink(SirenContract):
    rel: tuple[str, ...]
    href: str
    title: str
    media_type: Annotated[str, Field(serialization_alias="type")]
