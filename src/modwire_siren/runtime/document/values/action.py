from typing import Literal

from pydantic import Field

from ...contracts import Contract
from .field import SirenField


class SirenAction(Contract):
    """Describe an available Siren action."""

    class_: tuple[str, ...] = Field(default=(), alias="class")
    name: str
    method: Literal["DELETE", "GET", "PATCH", "POST", "PUT"] = "GET"
    href: str
    title: str | None = None
    type: str | None = None
    fields: tuple[SirenField, ...] = ()
