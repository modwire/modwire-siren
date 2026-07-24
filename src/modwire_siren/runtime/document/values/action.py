import json
from importlib.resources import files
from typing import ClassVar

from pydantic import Field, model_validator
from pydantic.json_schema import SkipJsonSchema

from ...contracts import Contract
from ...vocabulary import SirenActionMethod, SirenMediaType, SirenUri
from .field import SirenField


class SirenAction(Contract):
    """Describe an available Siren action."""

    default_media_type: ClassVar[SirenMediaType] = SirenMediaType.validate(
        json.loads(files("modwire_siren.runtime.document.schema").joinpath("siren.schema.json").read_text())["definitions"]
        ["Action"]["properties"]["type"]["default"]
    )
    class_: tuple[str, ...] | None = Field(default=None, alias="class")
    name: str
    method: SirenActionMethod = SirenActionMethod.GET
    href: SirenUri
    title: str | None = None
    type: SirenMediaType | SkipJsonSchema[None] = Field(default=None, json_schema_extra={"default": default_media_type})
    fields: tuple[SirenField, ...] | None = None

    @model_validator(mode="after")
    def apply_default_media_type(self) -> "SirenAction":
        if self.fields is not None and self.type is None:
            object.__setattr__(self, "type", self.default_media_type)
        return self
