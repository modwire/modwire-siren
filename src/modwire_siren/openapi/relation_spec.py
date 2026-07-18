from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SirenRelationSpec:
    """Declare one relation in an x-siren-resource extension."""

    rel: str
    resource: str
    many: bool
