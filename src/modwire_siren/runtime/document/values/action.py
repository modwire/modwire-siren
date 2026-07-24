from typing import Literal

from pydantic import Field

from ...contracts import Contract
from .field import SirenField


class SirenAction(Contract):
    """Describe an available Siren action."""

    class_: tuple[str, ...] | None = Field(default=None, alias="class")
    name: str
    method: Literal["DELETE", "GET", "PATCH", "POST", "PUT"] = "GET"
    href: str
    title: str | None = None
    type: str | None = None
    fields: tuple[SirenField, ...] | None = None
