from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class MessageCreate(BaseModel):
    role: str
    content: str

class ChatCreate(BaseModel):
    user_id: int
    messages: List[MessageCreate]

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    tokens: int
    created_at: datetime

class ChatResponse(BaseModel):
    id: int
    user_id: int
    title: Optional[str] = 'New chat'
    created_at: datetime
    messages: List[MessageResponse]
