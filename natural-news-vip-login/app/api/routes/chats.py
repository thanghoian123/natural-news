from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlmodel import Session
from app.database import get_db
from app.schemas.chat import ChatResponse, MessageResponse
from app.services.chat_service import create_chat, get_chat_history_by_id, get_chats_by_user_id,delete_chat_by_id
from app.services.llm_service import initialize_client_and_model, token_count, Workflow
from app.models.chat import Message, Chat
from typing import List
from app.services.workflows import get_good_workflow
import asyncio
from fastapi import WebSocketDisconnect
from starlette.websockets import WebSocketState
from app.services.websocket_manager import connection_manager

router = APIRouter(prefix="/chats", tags=["Chats"])

async def async_stream_iterator(sync_stream):
    """Convert a synchronous generator into an async generator."""
    loop = asyncio.get_running_loop()
    for chunk in sync_stream:
        yield await loop.run_in_executor(None, lambda: chunk)

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

@router.websocket("/ws/{chat_type}/{chat_id}")
async def chat_websocket(websocket: WebSocket, chat_type: str, chat_id: int, session: Session = Depends(get_db)):
    chat = session.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        await websocket.close(code=1008)  # Policy Violation
        return

    await connection_manager.connect(chat_id, websocket)
    
    try:
        while True:
            user_message = await websocket.receive_text()
            if not user_message.strip():
                continue  # Ignore empty messages

            user_tokens = token_count(user_message)
            message = Message(chat_id=chat_id, role="user", content=user_message, tokens=user_tokens)
            session.add(message)
            session.commit()

            assistant_response = ""

            if chat_type == "llm":
                client, model = initialize_client_and_model("Qwen2.5-72B-Instruct-32K")
                stream = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": user_message}],
                    stream=True,
                )

                async for chunk in async_stream_iterator(stream):
                    if websocket.client_state != WebSocketState.CONNECTED:  
                        print("Client disconnected, stopping stream.")
                        return  

                    if len(chunk.choices) > 0 and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        assistant_response += content
                        if content is not None:
                            await connection_manager.send_message(chat_id, content)

                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.close(code=1000)
                return

            elif chat_type == "ingredients-checker":
                analysis_workflow = Workflow(get_good_workflow(user_message))
                async for agent_response in analysis_workflow.run(user_message):
                    if chat_id not in connection_manager.active_connections:
                        break
                    assistant_response += agent_response
                    if agent_response is not None:
                        await connection_manager.send_message(chat_id, agent_response)

                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.close(code=1000)
                return

            assistant_tokens = token_count(assistant_response)
            message = Message(chat_id=chat_id, role="assistant", content=assistant_response, tokens=assistant_tokens)
            session.add(message)
            session.commit()

    except WebSocketDisconnect:
        print(f"Client {chat_id} disconnected.")
    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            await connection_manager.disconnect(chat_id)

