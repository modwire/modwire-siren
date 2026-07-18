from collections.abc import Mapping
from dataclasses import dataclass

from .relation_spec import SirenRelationSpec


@dataclass(frozen=True, slots=True)
class SirenResourceSpec:
    """Declare one x-siren-resource extension for an OpenAPI path template."""

    name: str
    path: str
    resource_class: str
    identifier: str
    path_parameters: Mapping[str, str]
    relations: Mapping[str, SirenRelationSpec]
    operations: tuple[str, ...] = ()
    collection_operations: tuple[str, ...] = ()
    collection_only: bool = False
    singleton: bool = False
    root_visible: bool | None = None
