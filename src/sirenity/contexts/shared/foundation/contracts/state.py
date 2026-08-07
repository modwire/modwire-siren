from pydantic import BaseModel, ConfigDict


class BaseState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", populate_by_name=True)
