from typing import Any

from pydantic import Field

from .base import SirenContract


class SirenRelation(SirenContract):
    field: str
    rel: str
    resource: str
    many: bool


class SirenResource(SirenContract):
    name: str
    path: str
    resource_class: str
    identifier: str
    path_parameters: dict[str, str]
    relations: tuple[SirenRelation, ...]
    operations: tuple[str, ...] = ()
    collection_operations: tuple[str, ...] = ()
    collection_only: bool = False
    profile: dict[str, Any] = Field(default_factory=dict)
