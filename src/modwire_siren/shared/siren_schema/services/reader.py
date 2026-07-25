import json
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache
from importlib.resources import files
from types import MappingProxyType
from typing import Any

from wireup import injectable

from ..values import SirenSchemaDocument


@injectable
@dataclass(frozen=True)
class SirenSchemaReader:
    """Load the pinned official Siren schema as an immutable document."""

    def document(self) -> SirenSchemaDocument:
        return self.official()

    @classmethod
    @cache
    def official(cls) -> SirenSchemaDocument:
        source = files("modwire_siren.shared.siren_schema.values").joinpath("siren.schema.json")
        return SirenSchemaDocument(value=cls.freeze(json.loads(source.read_text())))

    @classmethod
    def freeze(cls, value: Any) -> Any:
        if isinstance(value, Mapping):
            return MappingProxyType({key: cls.freeze(item) for key, item in value.items()})
        if isinstance(value, list):
            return tuple(cls.freeze(item) for item in value)
        return value
