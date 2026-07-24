from typing import Literal

from ...contracts import Contract
from .field_value import SirenFieldValue


class SirenField(Contract):
    """Describe an official Siren action field."""

    name: str
    type: Literal[
        "hidden",
        "text",
        "search",
        "tel",
        "url",
        "email",
        "password",
        "datetime",
        "date",
        "month",
        "week",
        "time",
        "datetime-local",
        "number",
        "range",
        "color",
        "checkbox",
        "radio",
        "file",
    ] = "text"
    title: str | None = None
    value: str | int | float | tuple[SirenFieldValue, ...] | None = None
