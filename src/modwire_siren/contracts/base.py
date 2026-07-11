from pydantic import BaseModel, ConfigDict


class SirenContract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
