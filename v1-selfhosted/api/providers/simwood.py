from datetime import datetime

import aiohttp as aiohttp
from aiohttp import BasicAuth
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import schemas
from auth.utils import get_webhook_user
from db import get_db
from sms import models
from providers.schemas import WebhookSuccess

router = APIRouter()


class SimwoodSMSData(BaseModel):
    time: datetime
    originator: str
    destination: str
    message: str
    length: int


class SimwoodSMSMessage(BaseModel):
    app: str
    id: str
    data: SimwoodSMSData


@router.post("/{user_id}/webhook", response_model=WebhookSuccess)
async def simwood_webhook(message: SimwoodSMSMessage, user: schemas.User = Depends(get_webhook_user),
                          db: Session = Depends(get_db)):
    conversation = db.query(models.Conversation).filter(models.Conversation.party == message.data.originator,
                                                        models.Conversation.user_id == user.id).first()
    if not conversation:
        conversation = models.Conversation(party=message.data.originator, user_id=user.id)
        db.add(conversation)

    message = models.Message(conversation=conversation, timestamp=message.data.time, message=message.data.message)
    db.add(message)
    db.commit()

    return WebhookSuccess(message_id=message.id)


async def send_message(user: schemas.APISettings, destination: str, message: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(f'https://api.simwood.com/v3/messaging/{user.api_account}/sms', json={
            "to": destination,
            "from": user.number,
            "message": message
        }, auth=BasicAuth(login=user.api_username, password=user.api_password)) as response:
            return await response.json()

