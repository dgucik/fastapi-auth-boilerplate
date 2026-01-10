from uuid import UUID

from pydantic import BaseModel


class MeResponse(BaseModel):
    id: UUID
    email: str
    username: str


class GetUserByIdResponse(BaseModel):
    id: UUID
    username: str
