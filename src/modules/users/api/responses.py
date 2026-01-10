from uuid import UUID

from pydantic import BaseModel


class MeResponse(BaseModel):
    """Response model for current user profile.

    Attributes:
        id: User UUID.
        email: User email address.
        username: User display name.
    """

    id: UUID
    email: str
    username: str


class GetUserByIdResponse(BaseModel):
    """Response model for fetching a user by ID.

    Attributes:
        id: User UUID.
        username: User display name.
    """

    id: UUID
    username: str
