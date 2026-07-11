from abc import ABC, abstractmethod

from ..contracts.action import SirenField
from ..contracts.operation import OpenApiField
from ..policies.field_type import SirenFieldTypeResolver
from ..standards import SirenFieldType


class SirenFieldFactory(ABC):
    @abstractmethod
    def create(self, field: OpenApiField) -> SirenField:
        raise NotImplementedError


class OpenApiSirenFieldFactory(SirenFieldFactory):
    def __init__(self, types: SirenFieldTypeResolver):
        self._types = types

    def create(self, field: OpenApiField) -> SirenField:
        field_type = self._types.resolve(field.schema_definition)
        return SirenField(
            name=field.name,
            type=field_type,
            required=field.required,
            title=field.schema_definition.get("title", field.name),
            options=tuple({"value": value, "title": str(value)} for value in field.schema_definition.get("enum", [])),
            schema=field.schema_definition if field_type is SirenFieldType.JSON else {},
        )
