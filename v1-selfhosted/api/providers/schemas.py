import uuid

from pydantic import BaseModel


class WebhookSuccess(BaseModel):
    message_id: uuid.UUID
    message: str = "Message stored successfully"
