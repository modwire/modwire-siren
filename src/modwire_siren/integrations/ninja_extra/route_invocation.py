from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class SirenRouteInvocation:
    request: Any
    path_values: dict[str, Any]
