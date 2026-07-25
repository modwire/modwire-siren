from pydantic import BaseModel, ConfigDict


class BaseValue(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)
