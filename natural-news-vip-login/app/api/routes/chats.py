from app.database import get_db
from app.schemas.chat import ChatResponse, MessageResponse
from app.services.chat_service import create_chat, get_chat_history_by_id, get_chats_by_user_id,delete_chat_by_id
from app.models.chat import Message
from app.services.websocket_manager import connection_manager
from app.services.llm_service import (
    get_message_history,
    handle_llm_chat,
    handle_ingredients_checker,
    validate_chat_and_user,
)
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlmodel import Session
from typing import List, Optional

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.post("/", response_model=ChatResponse)
def start_chat(user_id: int, session: Session = Depends(get_db)):
    """
    Create a new chat session for the given user.
    """
    return create_chat(session, user_id)

@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
def get_chat_messages(chat_id: int, session: Session = Depends(get_db)):
    """
    Retrieve chat history (messages) for a specific chat ID.
    """
    chat = get_chat_history_by_id(session, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat.messages

@router.delete("/{chat_id}", response_model=dict)
def delete_chat(chat_id: int, session: Session = Depends(get_db)):
    deleted = delete_chat_by_id(session, chat_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"message": "Chat deleted successfully"}

@router.get("/user/{user_id}", response_model=List[ChatResponse])
def get_user_chats(user_id: int, session: Session = Depends(get_db)):
    chats = get_chats_by_user_id(session, user_id)
    return chats


@router.websocket("/ws/{chat_type}/{chat_id}/{regenerate}")
@router.websocket("/ws/{chat_type}/{chat_id}")
async def chat_websocket(
    websocket: WebSocket,
    chat_type: str,
    chat_id: int,
    session: Session = Depends(get_db),
    regenerate: Optional[str] = None,
):
    await connection_manager.connect(chat_id, websocket)

    validated = await validate_chat_and_user(websocket, session, chat_id)
    if validated is None:
        return

    user = validated["user"]

    try:
        while True:
            user_message = await websocket.receive_text()

            # Use previous message for regeneration if requested
            if regenerate == "regenerate":
                last_message = (
                    session.query(Message)
                    .filter(Message.chat_id == chat_id, Message.role == "user")
                    .order_by(Message.created_at.desc())
                    .first()
                )
                if not last_message:
                    await websocket.send_text("❌ No previous message to regenerate.")
                    await websocket.close(code=1008)
                    return
                user_message = last_message.content

            if not user_message.strip():
                continue  # Ignore empty messages

            # Retrieve message history (last 5 messages)
            message_history = await get_message_history(session, chat_id)

            if chat_type == "llm":
                await handle_llm_chat(websocket, session, chat_id, user, message_history, user_message)
                return

            elif chat_type == "ingredients-checker":
                await handle_ingredients_checker(websocket, session, chat_id, user_message)
                return

            else:
                await websocket.send_text("❌ Unknown chat type.")
                await websocket.close(code=1008)
                return

    except WebSocketDisconnect:
        print(f"Client {chat_id} disconnected.")
    finally:
        await connection_manager.disconnect(chat_id)

