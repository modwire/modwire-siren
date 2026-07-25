from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from modwire_siren.shared import SirenRelation

from ...graph import SirenApi, SirenResource
from ...request import SirenContext


@dataclass(frozen=True)
class SirenProjectionRequest:
    api: SirenApi
    context: SirenContext
    resource: SirenResource | None
    value: Mapping[str, Any]
    rel: tuple[SirenRelation, ...] = ()
