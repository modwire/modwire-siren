from typing import Any

from ..contracts.entity import SirenEmbeddedEntity, SirenEntity
from ..contracts.link import SirenLink
from ..standards import SirenMediaType
from .document import ProfileDocument


class ProfileProjector:
    def __init__(self, profiles: ProfileDocument):
        self._profiles = profiles

    def project(self, entity: SirenEntity, metadata: dict[str, Any]) -> SirenEntity:
        normalized = self._profiles.prepare(
            entity.model_dump(mode="json", by_alias=True),
            metadata,
        )
        standard = self._profiles.standard
        profile_entity = SirenEmbeddedEntity(
            rel=(standard.relation,),
            entity=SirenEntity(
                classes=(standard.entity_class,),
                properties=normalized,
                links=(),
                actions=(),
                entities=(),
            ),
        )
        return entity.model_copy(
            update={
                "entities": (*entity.entities, profile_entity),
                "links": (
                    *entity.links,
                    SirenLink(
                        rel=("profile",),
                        href=standard.identifier,
                        title="Modwire Siren UI Profile",
                        media_type=SirenMediaType.ENTITY,
                    ),
                ),
            }
        )
