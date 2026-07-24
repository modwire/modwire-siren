from typing import Literal

from ..contracts import Contract


class SirenField(Contract):
    name: str
    type: Literal["checkbox", "date", "datetime-local", "email", "number", "text", "time", "url"]
