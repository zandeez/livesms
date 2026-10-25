from datetime import datetime

from aioredis.abc import AbcChannel
from aioredis.pubsub import Receiver
from fastapi import APIRouter, WebSocket, Depends, Request, HTTPException, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect
from typing import Dict, List
from uuid import UUID
import asyncio
import json

from auth.schemas import User
from auth.utils import get_current_user
from db import get_db, redis_conn
from sms import models, schemas
from sms.utils import get_websocket_user

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.lock = asyncio.Lock()
        self.redis = None
        self.receiver = None

    async def start(self):
        self.redis = await redis_conn()
        self.receiver = Receiver()
        await self.redis.subscribe(self.receiver.channel("rcon"))

        async def reader(receiver: Receiver):
            async for channel, msg in receiver.iter(decoder=json.loads, encoding='utf-8'):
                assert isinstance(channel, AbcChannel)
                try:
                    await self.notify_message(channel.name.decode("utf-8"), schemas.UpdateEvent(**msg))
                except Exception as e:
                    print(e)
                    print(msg)

        asyncio.create_task(reader(self.receiver))

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            if not self.active_connections[user_id]:
                await self.redis.subscribe(self.receiver.channel(user_id))
            self.active_connections[user_id].append(websocket)

    async def disconnect(self, user_id: str, websocket: WebSocket):
        async with self.lock:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                await self.redis.unsubscribe(user_id)

    async def notify_message(self, user_id: str, event: schemas.UpdateEvent):
        async with self.lock:
            if user_id in self.active_connections and self.active_connections[user_id]:
                await asyncio.gather(*[
                    x.send_text(event.json()) for x in self.active_connections[user_id]
                ])

    async def stop(self):
        async with self.lock:
            for k, v in self.active_connections.items():
                for connection in v:
                    await connection.close()
        self.redis.unsubscribe("rcon")
        self.receiver.stop()
        self.lock = None


connection_manager = ConnectionManager()


@router.on_event("startup")
async def start_manager():
    await connection_manager.start()


@router.on_event("shutdown")
async def stop_manager():
    await connection_manager.stop()


@router.get("/ticket", response_model=schemas.WebsocketTicketResponse)
async def create_ws_ticket(request: Request, user: User = Depends(get_current_user)):
    redis = await redis_conn()
    response_ticket = schemas.WebsocketTicketResponse()
    ticket_data = schemas.WebsocketTicketData(userId=user.id, ip=request.client.host)
    await redis.set(str(response_ticket.ticket), ticket_data.json(), expire=10)
    return response_ticket


@router.websocket("/ws")
async def new_message_notifications(websocket: WebSocket, user_id: UUID = Depends(get_websocket_user)):
    await connection_manager.connect(str(user_id), websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await connection_manager.disconnect(str(user_id), websocket)


@router.get("/conversations", response_model=schemas.ConversationListResponse)
async def load_conversations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversations = db.query(models.Conversation, func.max(models.Message.timestamp)).join(models.Message).filter(
        models.Conversation.user_id == user.id).group_by(models.Conversation.id).order_by(
        desc(func.max(models.Message.timestamp)))
    return_list = [
        schemas.Conversation(
            id=conversation[0].id,
            party=conversation[0].party,
            unreadCount=conversation[0].messages.filter(models.Message.timestamp > conversation[0].read).count(),
            read=conversation[0].read,
            lastMessage=getattr(conversation[0].messages.order_by(desc(models.Message.timestamp)).first(), "message", None)
        ) for conversation in conversations
    ]
    return schemas.ConversationListResponse(conversations=return_list)


@router.post("/conversations")
async def new_conversation(party: schemas.NewConversationRequest, user: User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    new_conversation = models.Conversation(
        party=party.party,
        user_id=user.id
    )
    db.add(new_conversation)
    db.commit()
    return schemas.Conversation.from_orm(new_conversation)


@router.delete("/conversations/{conversation_id}")
async def delete_message(conversation_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation: models.Conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id,
        models.Conversation.user_id == user.id).first()
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db.delete(conversation)
    db.commit()



@router.get("/conversations/{conversation_id}", response_model=schemas.SMSResponse)
async def get_messages(conversation_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id,
                                                        models.Conversation.user_id == user.id).first()
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return schemas.SMSResponse(messages=[
        schemas.SMSMessage.from_orm(x) for x in conversation.messages
    ])


@router.post("/conversations/{conversation_id}")
async def send_message(conversation_id: UUID, new_message: schemas.NewMessage, user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id,
                                                        models.Conversation.user_id == user.id).first()
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    message = models.Message(
        message=new_message.message,
        conversation=conversation,
        inbound=False
    )
    conversation.read = datetime.now()
    db.add(message)
    db.commit()


@router.post("/conversations/{conversation_id}/read")
async def conversation_read(conversation_id: UUID, user: User = Depends(get_current_user),
                            db: Session = Depends(get_db)):
    conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id,
                                                        models.Conversation.user_id == user.id).first()
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    conversation.read = datetime.now()
    db.commit()


@router.delete("/messages/{message_id}")
async def delete_message(message_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    with db.begin():
        message = db.query(models.Message).filter(models.Message.id == message_id,
                                                  models.Message.conversation.user_id == user.id).first()
        db.delete(message)
    db.expire(message)
