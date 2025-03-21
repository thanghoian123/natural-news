from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlmodel import Session
from app.database import get_db
from app.schemas.chat import ChatResponse, MessageResponse
from app.services.chat_service import create_chat, get_chat_history_by_id, get_chats_by_user_id
from app.services.llm_service import initialize_client_and_model, token_count, Workflow
from app.models.chat import Message, Chat
from typing import List
from app.services.workflows import get_good_workflow

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

@router.get("/user/{user_id}", response_model=List[ChatResponse])
def get_user_chats(user_id: int, session: Session = Depends(get_db)):
    """
    Retrieve all chat sessions associated with a user ID.
    """
    chats = get_chats_by_user_id(session, user_id)
    return chats

@router.websocket("/ws/{chat_type}/{chat_id}")
async def chat_websocket(websocket: WebSocket, chat_type: str, chat_id: int, session: Session = Depends(get_db)):
    """
    WebSocket endpoint for live chat interaction with the LLM.
    The chat session must already exist.
    """
    # Check if chat exists. (Optionally: validate the chat's user if you have authentication)
    chat = session.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        await websocket.close(code=1008)  # Policy Violation or custom close code
        return
    if chat_type == "llm":
        client, model = initialize_client_and_model("Qwen2.5-72B-Instruct-32K")
        await websocket.accept()

        # Receive user message (if your design expects only one message per connection)
        user_message = await websocket.receive_text()
        user_tokens = token_count(user_message)

        # Save user message
        message = Message(chat_id=chat_id, role="user", content=user_message, tokens=user_tokens)
        session.add(message)
        session.commit()

        # Stream response from LLM
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_message}],
            stream=True,
        )

        assistant_response = ""
        for chunk in stream:
            if len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                assistant_response += content
                await websocket.send_text(content)

        assistant_tokens = token_count(assistant_response)
        message = Message(chat_id=chat_id, role="assistant", content=assistant_response, tokens=assistant_tokens)
        session.add(message)
        session.commit()

        # Close the connection once the response is fully sent.
        await websocket.close()
    elif chat_type == "ingredients-checker":
        await websocket.accept()
        user_message = await websocket.receive_text()
        user_tokens = token_count(user_message)
        # Save user message
        message = Message(chat_id=chat_id, role="user", content=user_message, tokens=user_tokens)
        session.add(message)
        session.commit()

        good_workflow_agents = get_good_workflow(user_message)
        analysis_workflow = Workflow(good_workflow_agents)
        assistant_response = ""
        async for agent_response in analysis_workflow.run(user_message):
            assistant_response += agent_response
            await websocket.send_text(agent_response)  # Send each response chunk immediately

        assistant_tokens = token_count(assistant_response)
        message = Message(chat_id=chat_id, role="assistant", content=assistant_response, tokens=assistant_tokens)
        session.add(message)
        session.commit()
        await websocket.close()
