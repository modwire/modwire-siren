from ..contracts.collection import SirenCollectionRequest
from ..contracts.entity import SirenEmbeddedEntity, SirenEntity, SirenEntityRequest
from ..contracts.link import SirenLink
from ..openapi.catalog import SirenResourceCatalog
from ..openapi.error import OpenApiError
from ..openapi.href import SirenHrefResolver
from ..standards import SirenMediaType, SirenRelationName
from .action import SirenActionFactory
from .entity import SirenEntityFactory
from .pagination import SirenCollectionPaginationFactory, SirenPaginationHrefFactory


class SirenCollectionFactory:
    def __init__(
        self,
        catalog: SirenResourceCatalog,
        hrefs: SirenHrefResolver,
        entities: SirenEntityFactory,
        actions: SirenActionFactory,
        pagination_hrefs: SirenPaginationHrefFactory,
        pagination: SirenCollectionPaginationFactory,
    ):
        self._catalog = catalog
        self._hrefs = hrefs
        self._entities = entities
        self._actions = actions
        self._pagination_hrefs = pagination_hrefs
        self._pagination = pagination

    def create(self, request: SirenCollectionRequest) -> SirenEntity:
        if not request.collection_operation_ids:
            raise OpenApiError("Siren collection requests require at least one collection operation")
        self._pagination.validate(request.pagination)
        resource = self._catalog.resource(request.resource_name)
        collection_operations = tuple(
            self._catalog.operation(operation_id) for operation_id in request.collection_operation_ids
        )
        collection_path = self._collection_path(resource.path, resource.collection_only)
        foreign = tuple(
            operation.operation_id
            for operation in collection_operations
            if operation.path != collection_path
            and (
                operation.operation_id not in resource.collection_operations
                or not operation.path.startswith(f"{collection_path}/")
            )
        )
        if foreign:
            raise OpenApiError(f"Collection operations do not share path {collection_path!r}: {list(foreign)}")
        collection_href = self._hrefs.resolve(collection_path, request.path_values)
        items = tuple(dict(item) for item in request.items)
        return SirenEntity(
            classes=("collection", resource.resource_class),
            properties={"count": self._pagination.count(request.pagination, len(items))},
            links=tuple(
                SirenLink(
                    rel=(link.rel,),
                    href=self._pagination_hrefs.create(collection_href, link),
                    title=link.rel,
                    media_type=SirenMediaType.ENTITY,
                )
                for link in self._pagination.links(request.pagination)
            ),
            actions=tuple(
                self._actions.create(operation.operation_id, request.path_values) for operation in collection_operations
            ),
            entities=tuple(
                SirenEmbeddedEntity(
                    rel=(SirenRelationName.ITEM,),
                    entity=self._entities.create(
                        SirenEntityRequest(
                            resource_name=request.resource_name,
                            properties=item,
                            operation_ids=request.item_operation_ids,
                            path_values=dict(request.path_values),
                            entities=(),
                        )
                    ),
                )
                for item in items
            ),
        )

    @staticmethod
    def _collection_path(path: str, collection_only: bool) -> str:
        if collection_only:
            return path
        parent = path.rstrip("/").rsplit("/", 1)[0]
        return parent or "/"
