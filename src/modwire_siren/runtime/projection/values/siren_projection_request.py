from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ...siren_api import SirenApi
from ...siren_context import SirenContext
from ...siren_resource import SirenResource


@dataclass(frozen=True)
class SirenProjectionRequest:
    api: SirenApi
    context: SirenContext
    resource: SirenResource | None
    value: Mapping[str, Any]
    rel: tuple[str, ...] = ()
