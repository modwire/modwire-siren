from collections.abc import Mapping
from dataclasses import dataclass

from wireup import injectable

from modwire_siren.contexts.graph import SirenApi, SirenOperation, SirenResource, SirenResponse
from modwire_siren.contexts.shared import ModwireSirenError, SirenScope

from ...document import SirenDocument, SirenLink
from ...request import SirenContext, SirenResponseContext
from ...routing import SirenHrefService
from .projection import SirenProjectionService


@injectable
@dataclass(frozen=True)
class SirenResponseProjectionService:
    projection: SirenProjectionService
    hrefs: SirenHrefService

    def project(self, api: SirenApi, context: SirenResponseContext) -> SirenDocument:
        operation = self.operation(api, context.operation_id)
        response = self.response(operation, context)
        resource = self.resource(api, operation)
        self.validate_result(response, context.result)
        if context.status >= 400:
            return self.error(operation, resource, context)
        if context.representation == "root" and response.shape != "object":
            raise ModwireSirenError("Siren root response requires an OpenAPI object response")
        if response.shape == "empty":
            return self.empty(operation, resource, context)
        if response.shape == "array":
            if context.representation not in {None, "collection"}:
                raise ModwireSirenError("OpenAPI array response requires collection representation")
            return self.collection(api, resource, context)
        representation = context.representation
        if representation == "root":
            return self.root(api, operation, context)
        if (
            representation is None
            and operation.scope == SirenScope.ENTITY
            and resource is not None
            and resource.entity is not None
            and operation.route == resource.entity
        ):
            representation = "entity"
        if representation is None:
            raise ModwireSirenError(
                f"OpenAPI object response representation is ambiguous: {context.operation_id} {context.status}"
            )
        if representation == "entity":
            return self.entity(api, resource, context)
        if representation == "command":
            return self.command(operation, resource, context)
        raise ModwireSirenError("OpenAPI object response cannot use collection representation")

    def root(
        self, api: SirenApi, operation: SirenOperation, context: SirenResponseContext
    ) -> SirenDocument:
        if operation.scope != SirenScope.ROOT or not isinstance(context.result, Mapping):
            raise ModwireSirenError("Siren root response requires a root operation and mapping result")
        request = SirenContext(
            base_url=context.base_url,
            scope=SirenScope.ROOT,
            title=context.title,
            value=context.result,
            path_values=context.path_values,
            query=context.query,
            capabilities=context.capabilities,
        )
        return self.projection.project(api, request)

    def operation(self, api: SirenApi, operation_id: str) -> SirenOperation:
        matches = [operation for operation in api.operations if operation.name == operation_id]
        if len(matches) != 1:
            raise ModwireSirenError(f"Siren response references unknown operation: {operation_id}")
        return matches[0]

    def response(self, operation: SirenOperation, context: SirenResponseContext) -> SirenResponse:
        candidates = list(self.candidates(operation, context))
        if context.media_type is None and len(candidates) > 1:
            json_candidates = [response for response in candidates if response.media_type == "application/json"]
            candidates = json_candidates if len(json_candidates) == 1 else candidates
        if len(candidates) != 1:
            raise ModwireSirenError(
                f"Siren response requires exactly one status and media type match: "
                f"{operation.name} {context.status}"
            )
        return candidates[0]

    def has_response(self, api: SirenApi, context: SirenResponseContext) -> bool:
        operation = self.operation(api, context.operation_id)
        return bool(self.candidates(operation, context))

    def candidates(
        self, operation: SirenOperation, context: SirenResponseContext
    ) -> tuple[SirenResponse, ...]:
        exact = [response for response in operation.responses if response.status == str(context.status)]
        ranged = [
            response
            for response in operation.responses
            if len(response.status) == 3
            and response.status[0] == str(context.status)[0]
            and response.status[1:].upper() == "XX"
        ]
        defaults = [response for response in operation.responses if response.status == "default"]
        candidates = exact or ranged or defaults
        if context.media_type is not None:
            candidates = [response for response in candidates if response.media_type == context.media_type]
        return tuple(candidates)

    def project_error(
        self, api: SirenApi, context: SirenResponseContext, request_url: str | None = None
    ) -> SirenDocument:
        operation = self.operation(api, context.operation_id)
        resource = self.resource(api, operation)
        return self.error(operation, resource, context, request_url)

    def resource(self, api: SirenApi, operation: SirenOperation) -> SirenResource | None:
        if operation.resource is None:
            return None
        matches = [resource for resource in api.resources if resource.reference == operation.resource]
        if len(matches) != 1:
            raise ModwireSirenError(f"Siren operation references unknown resource: {operation.name}")
        return matches[0]

    def validate_result(self, response: SirenResponse, result: object) -> None:
        if response.shape == "empty" and result is not None:
            raise ModwireSirenError("OpenAPI content-free response requires a null result")
        if response.shape == "object" and not isinstance(result, Mapping):
            raise ModwireSirenError("OpenAPI object response requires a mapping result")
        if response.shape == "array" and (
            not isinstance(result, list) or any(not isinstance(item, Mapping) for item in result)
        ):
            raise ModwireSirenError("OpenAPI array response requires a list of mapping results")

    def entity(
        self, api: SirenApi, resource: SirenResource | None, context: SirenResponseContext
    ) -> SirenDocument:
        if resource is None or not isinstance(context.result, Mapping):
            raise ModwireSirenError("Siren entity response requires an operation-owned resource")
        request = SirenContext(
            base_url=context.base_url,
            resource=resource.name,
            title=context.title,
            value=context.result,
            relationships=context.relationships,
            path_values=context.path_values,
            query=context.query,
            capabilities=context.capabilities,
        )
        return self.projection.project_resource(api, request, resource)

    def collection(
        self, api: SirenApi, resource: SirenResource | None, context: SirenResponseContext
    ) -> SirenDocument:
        if resource is None or not isinstance(context.result, list):
            raise ModwireSirenError("Siren collection response requires an operation-owned resource")
        request = SirenContext(
            base_url=context.base_url,
            scope=SirenScope.COLLECTION,
            resource=resource.name,
            title=context.title,
            items=tuple(context.result),
            item_capabilities=context.item_capabilities,
            relationships=context.relationships,
            path_values=context.path_values,
            query=context.query,
            capabilities=context.capabilities,
        )
        return self.projection.project_resource(api, request, resource)

    def command(
        self, operation: SirenOperation, resource: SirenResource | None, context: SirenResponseContext
    ) -> SirenDocument:
        if not isinstance(context.result, Mapping):
            raise ModwireSirenError("Siren command response requires a mapping result")
        request = SirenContext(
            base_url=context.base_url,
            scope=SirenScope.ROOT,
            path_values=context.path_values,
            query=context.query,
        )
        return SirenDocument(
            class_=("command-result",),
            title=context.title or operation.title,
            properties=context.result,
            links=(SirenLink(
                rel=("self",),
                title=context.title or operation.title,
                href=self.hrefs.href(operation.route.path, request, resource, context.result),
            ),),
        )

    def empty(
        self, operation: SirenOperation, resource: SirenResource | None, context: SirenResponseContext
    ) -> SirenDocument:
        request = SirenContext(
            base_url=context.base_url,
            scope=SirenScope.ROOT,
            path_values=context.path_values,
            query=context.query,
        )
        return SirenDocument(
            class_=("empty",),
            title=context.title or operation.title,
            properties={"status": context.status},
            links=(SirenLink(
                rel=("self",),
                title=context.title or operation.title,
                href=self.hrefs.href(operation.route.path, request, resource),
            ),),
        )

    def error(
        self,
        operation: SirenOperation,
        resource: SirenResource | None,
        context: SirenResponseContext,
        request_url: str | None = None,
    ) -> SirenDocument:
        request = SirenContext(
            base_url=context.base_url,
            scope=SirenScope.ROOT,
            path_values=context.path_values,
            query=context.query,
        )
        properties = {"status": context.status}
        if isinstance(context.result, Mapping):
            properties = dict(context.result) | properties
        elif isinstance(context.result, list):
            properties["errors"] = context.result
        elif context.result is not None:
            properties["result"] = context.result
        return SirenDocument(
            class_=("error",),
            title=context.title or operation.title,
            properties=properties,
            links=(SirenLink(
                rel=("self",),
                title=context.title or operation.title,
                href=request_url or self.hrefs.href(operation.route.path, request, resource),
            ),),
        )
