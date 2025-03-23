from sqlalchemy.orm import Session
from app.models.chat import Chat
from datetime import datetime

def create_chat(db: Session, user_id: int) -> Chat:
    """
    Create a new chat for the given user.
    """
    chat = Chat(user_id=user_id)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

def get_chat_history_by_id(db: Session, chat_id: int) -> Chat:
    """
    Retrieve a chat and its messages by chat ID.
    """
    return db.query(Chat).filter(Chat.id == chat_id).first()

def get_chats_by_user_id(db: Session, user_id: int):
    """
    Retrieve all chats for a given user.
    """
    return db.query(Chat).filter(Chat.user_id == user_id).all()

def delete_chat_by_id(db: Session, chat_id: int) -> bool:
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        return False
    
    db.delete(chat)
    db.commit()
    return True