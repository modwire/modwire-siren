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
