from collections.abc import Sequence
from dataclasses import dataclass

from wireup import injectable

from ...capabilities import SirenCapabilityValidator
from ...document import SirenDocument
from ...graph import SirenApi
from ...request import SirenContext
from ...routing import SirenResourceResolver
from ...vocabulary import SirenScope
from ..contracts import SirenScopeProjector
from ..values import SirenProjectionRequest


@injectable
@dataclass(frozen=True)
class SirenProjectionService:
    projectors: Sequence[SirenScopeProjector]
    resources: SirenResourceResolver
    capabilities: SirenCapabilityValidator

    def project(self, api: SirenApi, context: SirenContext) -> SirenDocument:
        resource = None if context.scope == SirenScope.ROOT else self.resources.resolve(api, context)
        if resource is not None:
            self.capabilities.validate(resource, context)
        candidates = [projector for projector in self.projectors if projector.supports(context.scope)]
        if len(candidates) != 1:
            raise ValueError(f"Siren scope {context.scope!r} requires exactly one projector")
        return candidates[0].project(SirenProjectionRequest(api, context, resource, context.value))
