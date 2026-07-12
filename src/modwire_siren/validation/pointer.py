from collections.abc import Iterable
from typing import Any


class JsonPointer:
    @staticmethod
    def from_path(path: Iterable[Any]) -> str:
        parts = [JsonPointer.escape(str(part)) for part in path]
        return "/" + "/".join(parts) if parts else ""

    @staticmethod
    def join(pointer: str, value: str) -> str:
        return f"{pointer}/{JsonPointer.escape(value)}"

    @staticmethod
    def escape(value: str) -> str:
        return value.replace("~", "~0").replace("/", "~1")
