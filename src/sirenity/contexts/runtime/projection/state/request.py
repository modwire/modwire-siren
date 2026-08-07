from collections.abc import Mapping
from typing import Any

from sirenity.contexts.graph import SirenApi, SirenResource
from sirenity.contexts.shared import BaseState, SirenRelation

from ...request import SirenContext


class SirenProjectionRequest(BaseState):
    api: SirenApi
    context: SirenContext
    resource: SirenResource | None
    value: Mapping[str, Any]
    rel: tuple[SirenRelation, ...] = ()
