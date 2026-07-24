from typing import Any

from pydantic import AnyUrl, TypeAdapter
from pydantic_core import CoreSchema, core_schema


class SirenUri(str):
    """Represent an official Siren URI value."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: object, handler: Any) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema())

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: CoreSchema, handler: Any) -> dict[str, str]:
        return {"format": "uri", "type": "string"}

    @classmethod
    def validate(cls, value: str) -> "SirenUri":
        try:
            TypeAdapter(AnyUrl).validate_python(value)
        except ValueError as error:
            message = "Siren URI must be a valid URI."
            raise ValueError(message) from error
        return cls(value)
