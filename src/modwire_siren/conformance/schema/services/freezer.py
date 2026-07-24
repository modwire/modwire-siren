from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from wireup import injectable


@injectable
@dataclass(frozen=True)
class SirenSchemaFreezer:
    def freeze(self, value: Any) -> Any:
        if isinstance(value, Mapping):
            return MappingProxyType({key: self.freeze(item) for key, item in value.items()})
        if isinstance(value, list):
            return tuple(self.freeze(item) for item in value)
        return value
