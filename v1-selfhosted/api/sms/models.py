from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, event, Boolean, UniqueConstraint, desc
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import asyncio
import uuid

from auth.models import Base
from auth.schemas import APIType, APISettings
from sms import schemas
from sms.utils import notify_message_event
from providers.sinch import send_message as send_message_sinch
from providers.simwood import send_message as send_message_simwood


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (
        UniqueConstraint('user_id', 'party'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    party = Column(String(32), index=True, nullable=False)
    read = Column(DateTime(), index=True, nullable=False, default=datetime.now)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="conversations")

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", lazy='dynamic')


@event.listens_for(Conversation, 'after_insert')
def conversation_created(mapper, connection, target):
    asyncio.create_task(
        notify_message_event(target.user_id, schemas.EventType.NEW, schemas.ObjType.COV,
                             schemas.Conversation.from_orm(target)))


@event.listens_for(Conversation, 'after_update')
def conversation_updated(mapper, connection, target):
    conversation = schemas.Conversation.from_orm(target)
    conversation.unreadCount = target.messages.filter(Message.timestamp > target.read).count()
    conversation.lastMessage = getattr(target.messages.order_by(desc(Message.timestamp)).first(), "message", None)
    asyncio.create_task(notify_message_event(target.user_id, schemas.EventType.UPD, schemas.ObjType.COV,
                                             conversation))


@event.listens_for(Conversation, 'after_delete')
def conversation_deleted(mapper, connection, target):
    asyncio.create_task(notify_message_event(target.user_id, schemas.EventType.DEL, schemas.ObjType.COV,
                                             schemas.Conversation.from_orm(target)))


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    timestamp = Column(DateTime(), index=True, nullable=False, default=datetime.now)
    message = Column(String(1600), nullable=False)
    inbound = Column(Boolean(), nullable=False, default=True)

    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    conversation = relationship("Conversation", back_populates="messages")


@event.listens_for(Message, 'after_insert')
def message_created(mapper, connection, target):
    asyncio.create_task(notify_message_event(target.conversation.user_id, schemas.EventType.NEW, schemas.ObjType.MES,
                                             schemas.SMSMessage.from_orm(target)))

    if not target.inbound:
        if target.conversation.user.api_type == APIType.SINCH.value:
            asyncio.create_task(
                send_message_sinch(APISettings.from_orm(target.conversation.user), target.conversation.party,
                                   target.message))
        elif target.conversation.user.api_type == APIType.SIMWOOD.value:
            asyncio.create_task(
                send_message_simwood(APISettings.from_orm(target.conversation.user), target.conversation.party,
                                     target.message))
        else:
            pass


@event.listens_for(Message, 'after_update')
def message_updated(mapper, connection, target):
    asyncio.create_task(
        notify_message_event(target.conversation.user_id, schemas.EventType.UPD, schemas.ObjType.MES,
                             schemas.SMSMessage.from_orm(target)))


@event.listens_for(Message, 'after_delete')
def message_deleted(mapper, connection, target):
    asyncio.create_task(
        notify_message_event(target.conversation.user_id, schemas.EventType.DEL, schemas.ObjType.MES,
                             schemas.SMSMessage.from_orm(target)))
