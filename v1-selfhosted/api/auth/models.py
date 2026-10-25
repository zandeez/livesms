from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import secrets
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    username = Column(String(32), unique=True, index=True, nullable=False)
    password = Column(String(255))
    email = Column(String(255))
    number = Column(String(32), unique=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    api_type = Column(String(32), nullable=True)
    api_username = Column(String(64), nullable=True)
    api_password = Column(String(64), nullable=True)
    api_account = Column(String(64), nullable=True)
    # Shared secret included in the provider webhook URL, so only the provider can post inbound messages
    webhook_token = Column(String(64), nullable=False, default=lambda: secrets.token_urlsafe(32))

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
