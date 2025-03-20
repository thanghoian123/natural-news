from fastapi import APIRouter, Depends, WebSocket
from sqlmodel import Session
from app.database import get_db
from app.schemas.chat import ChatResponse
from app.services.chat_service import create_chat, get_chat_history
from app.services.llm_service import initialize_client_and_model, token_count
from app.models.chat import Message

router = APIRouter(prefix="/chats", tags=["Chats"])

@router.post("/", response_model=ChatResponse)
def start_chat(user_id: int, session: Session = Depends(get_db)):
    return create_chat(session, user_id)

@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(chat_id: int, session: Session = Depends(get_db)):
    return get_chat_history(session, chat_id)

@router.websocket("/ws/{chat_id}")
async def chat_websocket(websocket: WebSocket, chat_id: int, session: Session = Depends(get_db)):
    client, model = initialize_client_and_model("Qwen2.5-72B-Instruct-32K")
    await websocket.accept()
    while True:
        user_message = await websocket.receive_text()
        user_tokens = token_count(user_message)
        
        message = Message(chat_id=chat_id, role="user", content=user_message, tokens=user_tokens)
        session.add(message)
        session.commit()
        
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_message}],
            stream=True,
        )
        
        assistant_response = ""
        async for chunk in stream:
            if len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
                assistant_response += chunk.choices[0].delta.content
                await websocket.send_text(chunk.choices[0].delta.content)
        
        assistant_tokens = token_count(assistant_response)
        message = Message(chat_id=chat_id, role="assistant", content=assistant_response, tokens=assistant_tokens)
        session.add(message)
        session.commit()