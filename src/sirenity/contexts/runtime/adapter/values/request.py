from collections.abc import Mapping

from pydantic import Field, JsonValue, model_validator

from sirenity.contexts.shared import BaseValue, ModwireSirenError, SirenMediaType

from .policy import SirenAdapterPolicy


class SirenAdapterRequest(BaseValue):
    """Describe one already-executed HTTP operation for Siren projection.

    Pass the framework's executed `operation_id` when it is available. Otherwise provide `method`
    and `path` so the adapter can resolve the operation from its startup-compiled route catalogue.
    `result` is the already-produced application value: the adapter never redispatches the operation.
    """

    status: int
    result: JsonValue = None
    base_url: str
    operation_id: str | None = None
    method: str | None = None
    path: str | None = None
    request_url: str | None = None
    media_type: SirenMediaType | None = None
    path_values: Mapping[str, JsonValue] = Field(default_factory=dict)
    query: tuple[tuple[str, JsonValue], ...] = ()
    headers: Mapping[str, str] = Field(default_factory=dict)
    policy: SirenAdapterPolicy = Field(default_factory=SirenAdapterPolicy)

    @model_validator(mode="after")
    def validate_request(self) -> "SirenAdapterRequest":
        if not 100 <= self.status <= 599:
            raise ModwireSirenError("Siren adapter status must be between 100 and 599")
        if self.operation_id is None and ((self.method is None) != (self.path is None)):
            raise ModwireSirenError("Siren adapter route resolution requires both method and path")
        if self.operation_id is None and self.path is None and self.status < 400:
            raise ModwireSirenError("A successful Siren adapter response requires an operation")
        return self
