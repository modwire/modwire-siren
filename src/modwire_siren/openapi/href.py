import re
from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any
from urllib.parse import quote, urljoin

from .error import OpenApiError


class SirenHrefResolver(ABC):
    @abstractmethod
    def resolve(self, path: str, values: Mapping[str, Any]) -> str:
        raise NotImplementedError


class OpenApiHrefResolver(SirenHrefResolver):
    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/") + "/"

    def resolve(self, path: str, values: Mapping[str, Any]) -> str:
        resolved = path
        for name in re.findall(r"{([^}]+)}", path):
            if name not in values:
                raise OpenApiError(f"Missing path value {name!r} for {path}")
            resolved = resolved.replace(f"{{{name}}}", quote(str(values[name]), safe=""))
        return urljoin(self._base_url, resolved.lstrip("/"))
