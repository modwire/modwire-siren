from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SirenRelationSpec:

    rel: str
    resource: str
    many: bool
