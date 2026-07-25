from __future__ import annotations

from collections.abc import Mapping

from pydantic import Field, JsonValue

from ...contracts import Contract
from .action import SirenAction
from .link import SirenLink


class SirenEntity(Contract):
    class_: tuple[str, ...] | None = Field(default=None, alias="class")
    title: str | None = None
    properties: Mapping[str, JsonValue] | None = None
    actions: tuple[SirenAction, ...] | None = None
    links: tuple[SirenLink, ...] | None = None
