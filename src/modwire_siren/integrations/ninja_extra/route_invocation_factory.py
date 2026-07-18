import inspect
from typing import Any

from .route_invocation import SirenRouteInvocation


class SirenRouteInvocationFactory:
    def __init__(self, signature: inspect.Signature):
        self._signature = signature

    def create(self, controller: Any, args: tuple[Any, ...], kwargs: dict[str, Any]) -> SirenRouteInvocation:
        arguments = self._signature.bind(controller, *args, **kwargs).arguments
        request = arguments.get("request", controller)
        path_values = {name: value for name, value in arguments.items() if name not in {"self", "request"}}
        return SirenRouteInvocation(request=request, path_values=path_values)
