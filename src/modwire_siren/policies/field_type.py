from abc import ABC, abstractmethod
from typing import ClassVar

from ..standards import SirenFieldType


class SirenFieldTypeResolver(ABC):
    @abstractmethod
    def resolve(self, schema: dict) -> SirenFieldType:
        raise NotImplementedError


class OpenApiSirenFieldTypeResolver(SirenFieldTypeResolver):
    TYPE_MAP: ClassVar = {
        "boolean": SirenFieldType.CHECKBOX,
        "integer": SirenFieldType.NUMBER,
        "string": SirenFieldType.TEXT,
    }

    def resolve(self, schema: dict) -> SirenFieldType:
        kind = schema.get("type", "string")
        if kind in {"array", "object"} or "anyOf" in schema:
            return SirenFieldType.JSON
        return self.TYPE_MAP.get(kind, SirenFieldType.TEXT)
