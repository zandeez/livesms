from datetime import datetime
from typing import Optional

import aiohttp
from fastapi import APIRouter, Depends
from pydantic.main import BaseModel
from sqlalchemy.orm import Session

from auth import schemas
from auth.utils import get_webhook_user
from db import get_db
from providers.schemas import WebhookSuccess
from sms import models

router = APIRouter()


class SinchSMSMessage(BaseModel):
    class Config:
        fields = {
            'from_': 'from'
        }

    type: str
    id: str
    from_: str
    to: str
    body: str
    operator_id: Optional[str]
    sent_at: Optional[datetime]
    received_at: datetime


@router.post("/{user_id}/webhook", response_model=WebhookSuccess)
async def sinch_webhook(message: SinchSMSMessage, user: schemas.User = Depends(get_webhook_user),
                        db: Session = Depends(get_db)):
    conversation = db.query(models.Conversation).filter(models.Conversation.party == message.from_,
                                                        models.Conversation.user_id == user.id).first()
    if not conversation:
        conversation = models.Conversation(party=message.from_, user_id=user.id)
        db.add(conversation)

    message = models.Message(conversation=conversation, timestamp=message.received_at, message=message.body)
    db.add(message)
    db.commit()

    return WebhookSuccess(message_id=message.id)


async def send_message(user: schemas.APISettings, destination: str, message: str):
    async with aiohttp.ClientSession(
            headers={'Authorization': f'Bearer {user.api_password}'}) as session:
        async with session.post(f'https://eu.sms.api.sinch.com/xms/v1/{user.api_account}/batches', json={
            "to": [destination],
            "from": user.number,
            "body": message,
            "type": "mt_text"
        }) as response:
            res_body = await response.read()
            return res_body