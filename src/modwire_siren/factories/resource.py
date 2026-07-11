from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from ..contracts.resource import SirenResource
from ..openapi.error import OpenApiError
from ..openapi.href import SirenHrefResolver


class SirenResourceHrefResolver(ABC):
    @abstractmethod
    def href(self, resource: SirenResource, values: Mapping[str, Any]) -> str:
        raise NotImplementedError

    @abstractmethod
    def path_values(self, resource: SirenResource, values: Mapping[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class OpenApiSirenResourceHrefResolver(SirenResourceHrefResolver):
    def __init__(self, hrefs: SirenHrefResolver):
        self._hrefs = hrefs

    def href(self, resource: SirenResource, values: Mapping[str, Any]) -> str:
        return self._hrefs.resolve(resource.path, self.path_values(resource, values))

    def path_values(self, resource: SirenResource, values: Mapping[str, Any]) -> dict[str, Any]:
        missing = set(resource.path_parameters.values()) - set(values)
        if missing:
            raise OpenApiError(f"Missing properties {sorted(missing)} for resource {resource.name!r}")
        return {parameter: values[property_name] for parameter, property_name in resource.path_parameters.items()}
