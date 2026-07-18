from collections.abc import Iterable, Mapping
from dataclasses import asdict, is_dataclass
from typing import Any, Protocol


class SirenPropertySerializer(Protocol):
    """Serialize framework return values into Siren property mappings."""

    def serialize(self, value: Any) -> Mapping[str, Any]:
        raise NotImplementedError


class DefaultSirenPropertySerializer:
    """Serialize common framework-neutral property containers."""

    def serialize(self, value: Any) -> Mapping[str, Any]:
        if isinstance(value, Mapping):
            return dict(value)
        if is_dataclass(value) and not isinstance(value, type):
            return self._mapping(asdict(value), "dataclass")
        model_dump = getattr(value, "model_dump", "")
        if callable(model_dump):
            return self._mapping(model_dump(), "model_dump")
        legacy_dict = getattr(value, "dict", "")
        if callable(legacy_dict):
            return self._mapping(legacy_dict(), "dict")
        raise TypeError(
            "Siren property serialization requires a mapping, dataclass, or object with model_dump()/dict(); "
            f"received {type(value).__name__}"
        )

    @staticmethod
    def _mapping(value: Any, source: str) -> Mapping[str, Any]:
        if not isinstance(value, Mapping):
            raise TypeError(f"Siren property serializer {source} returned {type(value).__name__}, not a mapping")
        return dict(value)


DEFAULT_PROPERTY_SERIALIZER = DefaultSirenPropertySerializer()


def serialize_collection_items(serializer: SirenPropertySerializer, items: Any) -> tuple[Mapping[str, Any], ...]:
    if isinstance(items, (str, bytes, Mapping)) or not isinstance(items, Iterable):
        raise TypeError("Siren collection serialization requires an iterable of items")
    return tuple(serializer.serialize(item) for item in items)
