from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List, Optional
from app.models.user import User

class Chat(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="chats")
    
    messages: List["Message"] = Relationship(back_populates="chat")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    chat_id: int = Field(foreign_key="chat.id")
    role: str  # "user" or "assistant"
    content: str
    tokens: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    chat: Chat = Relationship(back_populates="messages")
