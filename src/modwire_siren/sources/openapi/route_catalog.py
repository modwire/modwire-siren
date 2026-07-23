from typing import Any

from .resource import Resource


class RouteCatalog:
    def __init__(self, paths: dict[str, Any]) -> None:
        self.paths = paths
        self.resource_list = self.compile_resources()

    def resources(self) -> tuple[Resource, ...]:
        return self.resource_list

    def compile_resources(self) -> tuple[Resource, ...]:
        candidates: dict[str, Resource] = {}
        names: dict[tuple[str, tuple[str, ...]], str] = {}
        for path in self.paths:
            segments = self.segments(path)
            collection_path: str | None = None
            entity_path: str | None = None
            if self.is_collection(segments):
                collection_path = path
            elif self.is_entity(segments):
                collection_path = "/" + "/".join(segments[:-1])
                entity_path = path
            if collection_path is None:
                continue
            name = self.singular(segments[-1] if entity_path is None else segments[-2])
            selection = name, self.parameters(collection_path)
            existing_path = names.get(selection)
            if existing_path is not None and existing_path != collection_path:
                raise ValueError(
                    f"OpenAPI routes derive duplicate resource {name!r}: {existing_path!r} and {collection_path!r}"
                )
            names[selection] = collection_path
            existing = candidates.get(collection_path)
            if existing is None:
                candidates[collection_path] = Resource(
                    collection_path,
                    name,
                    name.replace("_", "-"),
                    collection_path,
                    entity_path,
                    "id",
                )
            elif entity_path is not None:
                candidates[collection_path] = Resource(
                    existing.reference,
                    existing.name,
                    existing.resource_class,
                    existing.collection_path,
                    entity_path,
                    existing.identifier,
                )
        return tuple(candidates.values())

    def ownership(self, path: str) -> tuple[Resource, str]:
        candidates: list[tuple[int, Resource, str]] = []
        for resource in self.resource_list:
            if resource.entity_path and self.belongs(path, resource.entity_path):
                candidates.append((len(self.segments(resource.entity_path)), resource, "entity"))
            if self.belongs(path, resource.collection_path):
                candidates.append((len(self.segments(resource.collection_path)), resource, "collection"))
        if not candidates:
            raise ValueError(f"OpenAPI route is unsupported: {path!r}")
        longest = max(candidate[0] for candidate in candidates)
        owners = [(resource, scope) for length, resource, scope in candidates if length == longest]
        if len(owners) != 1:
            raise ValueError(f"OpenAPI route ownership is ambiguous: {path!r}")
        return owners[0]

    def belongs(self, path: str, base: str) -> bool:
        path_segments = self.segments(path)
        base_segments = self.segments(base)
        return path_segments[: len(base_segments)] == base_segments and self.parameters(path) == self.parameters(base)

    def segments(self, path: str) -> tuple[str, ...]:
        if path == "/":
            return ()
        if not isinstance(path, str) or not path.startswith("/"):
            raise ValueError(f"OpenAPI route is unsupported: {path!r}")
        normalized = path[:-1] if path.endswith("/") else path
        segments = tuple(normalized[1:].split("/"))
        if any(
            not segment or (("{" in segment or "}" in segment) and not self.is_parameter(segment))
            for segment in segments
        ):
            raise ValueError(f"OpenAPI route is unsupported: {path!r}")
        return segments

    def is_collection(self, segments: tuple[str, ...]) -> bool:
        return bool(segments) and not self.is_parameter(segments[-1]) and self.is_plural(segments[-1])

    def is_entity(self, segments: tuple[str, ...]) -> bool:
        return len(segments) > 1 and self.is_parameter(segments[-1]) and self.is_plural(segments[-2])

    def is_parameter(self, segment: str) -> bool:
        return len(segment) > 2 and segment.startswith("{") and segment.endswith("}")

    def parameters(self, path: str) -> tuple[str, ...]:
        return tuple(segment[1:-1] for segment in self.segments(path) if self.is_parameter(segment))

    def is_plural(self, value: str) -> bool:
        return value.endswith("s") and len(value) > 1

    def singular(self, value: str) -> str:
        normalized = value.replace("-", "_")
        if normalized.endswith("ies"):
            return f"{normalized[:-3]}y"
        if self.is_plural(normalized):
            return normalized[:-1]
        raise ValueError(f"OpenAPI collection path must be plural: {value!r}")
