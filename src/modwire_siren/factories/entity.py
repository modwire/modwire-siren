from ..contracts.entity import SirenEntity, SirenEntityRequest
from ..openapi.catalog import SirenResourceCatalog
from ..openapi.error import OpenApiError
from ..profile.projection import ProfileProjector
from .action import SirenActionFactory
from .link import SirenLinkFactory
from .resource import SirenResourceHrefResolver


class SirenEntityFactory:
    def __init__(
        self,
        catalog: SirenResourceCatalog,
        hrefs: SirenResourceHrefResolver,
        links: SirenLinkFactory,
        actions: SirenActionFactory,
        profiles: ProfileProjector,
    ):
        self._catalog = catalog
        self._hrefs = hrefs
        self._links = links
        self._actions = actions
        self._profiles = profiles

    def create(self, request: SirenEntityRequest) -> SirenEntity:
        resource = self._catalog.resource(request.resource_name)
        operations = tuple(self._catalog.operation(operation_id) for operation_id in request.operation_ids)
        foreign = tuple(operation.operation_id for operation in operations if operation.path != resource.path)
        if foreign:
            raise OpenApiError(f"Operations {list(foreign)} do not belong to resource {resource.name!r}")
        values = request.properties | request.path_values
        operation_values = self._hrefs.path_values(resource, values)
        entity = SirenEntity(
            classes=(resource.resource_class,),
            properties=request.properties,
            links=self._links.create(resource, values),
            actions=tuple(
                self._actions.create(operation.operation_id, operation_values) for operation in operations
            ),
            entities=request.entities,
        )
        if not resource.profile:
            return entity
        return self._profiles.project(entity, resource.profile)
