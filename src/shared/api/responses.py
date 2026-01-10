from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Generic message response model.

    Attributes:
        message: Response message content.
    """

    message: str
