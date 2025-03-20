from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from app.models.chat import Chat
from datetime import datetime

def create_chat(db: Session, user_id: int):
    chat = Chat(user_id=user_id)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

def get_chat_history(db: Session, chat_id: int):
    return db.exec(select(Chat).where(Chat.id == chat_id)).first()