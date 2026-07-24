import re
from dataclasses import dataclass

from wireup import injectable

from ...document import SirenDocument, SirenLink
from ...routing import SirenHrefService
from ...vocabulary import SirenHttpMethod, SirenScope
from ..contracts import SirenActionDocumentService, SirenScopeProjector
from ..values import SirenProjectionRequest

_PARAMETER = re.compile(r"\{([^}]+)\}")


@injectable(as_type=SirenScopeProjector, qualifier=SirenScope.ROOT)
@dataclass(frozen=True)
class SirenRootScopeProjector(SirenScopeProjector):
    actions: SirenActionDocumentService
    hrefs: SirenHrefService

    def supports(self, scope: SirenScope) -> bool:
        return scope == SirenScope.ROOT

    def project(self, request: SirenProjectionRequest) -> SirenDocument:
        operations = {operation.name: operation for operation in request.api.operations}
        links = [SirenLink(rel=("self",), href=self.hrefs.href(request.api.root.route.path, request.context, None))]
        links.extend(
            SirenLink(
                rel=(resource.name,),
                href=self.hrefs.href(resource.collection.path, request.context, resource, include_query=False),
            )
            for resource in request.api.resources
            if not _PARAMETER.search(resource.collection.path)
            and any(
                operation.scope == SirenScope.COLLECTION
                and operation.route.path == resource.collection.path
                and operation.method == SirenHttpMethod.GET
                for operation in request.api.operations
            )
        )
        actions = [
            self.actions.action(operations[name], request.context, None, {}, include_query=False)
            for name in request.api.root.operations
            if name in request.context.capabilities
        ]
        return SirenDocument(class_=("api", "entry-point"), links=tuple(links), actions=tuple(actions) or None)
