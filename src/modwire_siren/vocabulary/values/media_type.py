import re
from typing import Any

from pydantic_core import CoreSchema, core_schema

from ...siren_schema import SirenSchemaReader


class SirenMediaType(str):
    """Represent an official Siren media type."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: object, handler: Any) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema())

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: CoreSchema, handler: Any) -> dict[str, Any]:
        return cls.schema()

    @classmethod
    def validate(cls, value: str) -> "SirenMediaType":
        if re.fullmatch(cls.schema()["pattern"], value) is None:
            message = "Siren media type must use the official media-type grammar."
            raise ValueError(message)
        return cls(value)

    @classmethod
    def default(cls) -> "SirenMediaType":
        return cls.validate(SirenSchemaReader.official().default("Action", "type"))

    @classmethod
    def schema(cls) -> dict[str, Any]:
        document = SirenSchemaReader.official()
        return document.thaw(document.definition("MediaType"))
