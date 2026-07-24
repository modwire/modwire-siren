import json
from importlib.resources import files
from typing import Any

from pydantic_core import CoreSchema, core_schema

from .uri import SirenUri


class SirenRelation(str):
    """Represent an official Siren relation value."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: object, handler: Any) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema())

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: CoreSchema, handler: Any) -> dict[str, Any]:
        return cls.schema()

    @classmethod
    def validate(cls, value: str) -> "SirenRelation":
        if value in cls.registered():
            return cls(value)
        try:
            SirenUri.validate(value)
        except ValueError as error:
            message = "Siren relation must be an official relation token or URI."
            raise ValueError(message) from error
        return cls(value)

    @classmethod
    def registered(cls) -> frozenset[str]:
        values = cls.schema()["anyOf"][1]["enum"]
        return frozenset(values)

    @classmethod
    def schema(cls) -> dict[str, Any]:
        document = json.loads(files("modwire_siren.runtime.document.schema").joinpath("siren.schema.json").read_text())
        return document["definitions"]["RelValue"]
