from datetime import datetime
from enum import Enum
from ipaddress import IPv6Address, IPv4Address

from pydantic import BaseModel
from typing import List, Union, Optional
import uuid


class Conversation(BaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        fields = {
            'userId': 'user_id'
        }

    id: uuid.UUID
    party: str
    read: datetime
    unreadCount: int = 0
    lastMessage: Optional[str]


class ConversationListResponse(BaseModel):
    conversations: List[Conversation]


class NewConversationRequest(BaseModel):
    party: str


class SMSMessage(BaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        fields = {
            'conversationId': 'conversation_id'
        }

    id: uuid.UUID
    timestamp: datetime
    message: str
    inbound: bool
    conversationId: uuid.UUID


class NewMessage(BaseModel):
    message: str


class WebsocketTicketData(BaseModel):
    ip: Union[IPv4Address, IPv6Address]
    userId: uuid.UUID


class WebsocketTicketResponse(BaseModel):
    ticket: uuid.UUID = uuid.uuid4()


class SMSResponse(BaseModel):
    messages: List[SMSMessage]


class EventType(Enum):
    NEW = "new"
    UPD = "upd"
    DEL = "del"


class ObjType(Enum):
    COV = "conversation"
    MES = "message"


class UpdateEvent(BaseModel):
    event: EventType
    objectType: ObjType
    objectId: uuid.UUID
    instance: Union[Conversation, SMSMessage, None]
