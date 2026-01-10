from pydantic import BaseModel


class UpdateMeRequest(BaseModel):
    username: str


class UpdateUserIdRequest(BaseModel):
    username: str
