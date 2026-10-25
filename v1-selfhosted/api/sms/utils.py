import json
import uuid
from typing import Union

from fastapi import HTTPException, status, WebSocket

from db import redis_conn
from sms import schemas
from sms.schemas import WebsocketTicketData


async def get_websocket_user(ticket: str, request: WebSocket):
    redis = await redis_conn()
    # Tickets are single use: read and delete atomically
    transaction = redis.multi_exec()
    ticket_get = transaction.get(ticket)
    transaction.delete(ticket)
    await transaction.execute()
    ticket = await ticket_get
    if ticket:
        ticket_data = WebsocketTicketData(**json.loads(ticket))
        if request.client.host == str(ticket_data.ip):
            return ticket_data.userId
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


async def notify_message_event(user_id: uuid.UUID, event_type: schemas.EventType, object_type: schemas.ObjType,
                               instance: Union[schemas.Conversation, schemas.SMSMessage, None]):
    redis = await redis_conn()
    message_event = schemas.UpdateEvent(
        event=event_type,
        objectId=instance.id,
        objectType=object_type
    )
    if event_type != schemas.EventType.DEL:
        message_event.instance = instance
    await redis.publish(str(user_id), message_event.json())
