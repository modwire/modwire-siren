from typing import Any, ClassVar

from pydantic_core import CoreSchema, PydanticCustomError, core_schema


class SirenActionMethod(str):
    """Represent an official Siren action method."""

    default_value: ClassVar[str] = "GET"
    official_values: ClassVar[tuple[str, ...]] = ("DELETE", "GET", "PATCH", "POST", "PUT")

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: object, handler: Any) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema())

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: CoreSchema, handler: Any) -> dict[str, Any]:
        return cls.schema()

    @classmethod
    def default(cls) -> "SirenActionMethod":
        return cls.validate(cls.default_value)

    @classmethod
    def values(cls) -> frozenset[str]:
        return frozenset(cls.official_values)

    @classmethod
    def validate(cls, value: str) -> "SirenActionMethod":
        if value not in cls.values():
            raise PydanticCustomError("enum", "Siren action method must be an official method.")
        return cls(value)

    @classmethod
    def schema(cls) -> dict[str, Any]:
        return {
            "default": cls.default_value,
            "description": (
                "An enumerated attribute mapping to a protocol method. For HTTP, these values may be GET, PUT, "
                "POST, DELETE, or PATCH. As new methods are introduced, this list can be extended. If this "
                "attribute is omitted, GET should be assumed."
            ),
            "enum": list(cls.official_values),
            "type": "string",
        }
