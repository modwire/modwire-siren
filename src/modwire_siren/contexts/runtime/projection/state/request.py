from collections.abc import Mapping
from typing import Any

from modwire_siren.shared import BaseState, SirenRelation

from ...graph import SirenApi, SirenResource
from ...request import SirenContext


class SirenProjectionRequest(BaseState):
    api: SirenApi
    context: SirenContext
    resource: SirenResource | None
    value: Mapping[str, Any]
    rel: tuple[SirenRelation, ...] = ()
