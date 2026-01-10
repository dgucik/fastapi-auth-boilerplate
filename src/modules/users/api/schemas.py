from pydantic import BaseModel


class UpdateMeRequest(BaseModel):
    username: str
