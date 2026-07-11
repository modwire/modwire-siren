from abc import ABC, abstractmethod
from typing import Any

from .contracts.entity import SirenEntity


class SirenSerializer(ABC):
    @abstractmethod
    def serialize(self, entity: SirenEntity) -> dict[str, Any]:
        raise NotImplementedError


class PydanticSirenSerializer(SirenSerializer):
    def serialize(self, entity: SirenEntity) -> dict[str, Any]:
        return entity.model_dump(mode="json", by_alias=True)
