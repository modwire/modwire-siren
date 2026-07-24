from typing import Any

from pydantic_core import CoreSchema, PydanticCustomError, core_schema

from ....siren_schema import SirenSchemaReader


class SirenActionMethod(str):
    """Represent an official Siren action method."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: object, handler: Any) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema())

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: CoreSchema, handler: Any) -> dict[str, Any]:
        return cls.schema()

    @classmethod
    def default(cls) -> "SirenActionMethod":
        return cls.validate(SirenSchemaReader.official().default("Action", "method"))

    @classmethod
    def values(cls) -> frozenset[str]:
        return frozenset(SirenSchemaReader.official().enum("Action", "method"))

    @classmethod
    def validate(cls, value: str) -> "SirenActionMethod":
        if value not in cls.values():
            raise PydanticCustomError("enum", "Siren action method must be an official method.")
        return cls(value)

    @classmethod
    def schema(cls) -> dict[str, Any]:
        document = SirenSchemaReader.official()
        return document.thaw(document.member("Action", "method"))
