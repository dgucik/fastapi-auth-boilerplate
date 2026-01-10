from pydantic import BaseModel


class UpdateMeRequest(BaseModel):
    """Request model for updating current user profile.

    Attributes:
        username: New display name.
    """

    username: str


class UpdateUserIdRequest(BaseModel):
    """Request model for updating another user's profile.

    Attributes:
        username: New display name.
    """

    username: str
