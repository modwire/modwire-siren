from pydantic import BaseModel


class RenameWidgetPayload(BaseModel):
    title: str
