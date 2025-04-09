from app.core.config import API_KEY
from app.schemas.user import TierEnum
from app.models.chat import Message, Chat
from app.models.user import User
from app.services.workflows import get_good_workflow
from app.services.websocket_manager import connection_manager
from app.services.prompt import TEXT_SUMMARIZER, JOURNALS, LONGEVITY_ROADMAP, MASTER_GARDENER, PERSONALIZED_WELLNESS_PLAN , NATURAL_SUPPLEMENTS_INGREDIENTS_FINDER, GROCERY_SHOPPING_COACH, DAILY_MEAL_PLANNER, INGREDIENTS_CHECKER

import asyncio
from openai import OpenAI
import tiktoken
from typing import AsyncGenerator, List, Optional, Dict
from sqlmodel import Session
from starlette.websockets import WebSocketState
from fastapi import WebSocket

map_tools_name = {
    "text-summarizer": TEXT_SUMMARIZER,
    "journals": JOURNALS,
    "longevity-roadmap": LONGEVITY_ROADMAP,
    "master-gardener": MASTER_GARDENER,
    "personalized-wellness-plan": PERSONALIZED_WELLNESS_PLAN,
    "natural-supplements-ingredients-finder": NATURAL_SUPPLEMENTS_INGREDIENTS_FINDER,
    "grocery-shopping-coach": GROCERY_SHOPPING_COACH,
    "daily-meal-planner": DAILY_MEAL_PLANNER,
    "ingredients-checker": INGREDIENTS_CHECKER,
    "chat-with-enoch": "You are a helpful assistant."
}

def initialize_client_and_model(llm_selection):
    """Initialize the client and model based on the selected LLM engine."""
    if llm_selection == "Enoch-RC-14-128K":
        client = OpenAI(
            base_url="http://35.170.240.5:8081",
            api_key=API_KEY
        )
        model = 'LLaMA_CPP'
    elif llm_selection == "Qwen2.5-72B-Instruct-32K":
        client = OpenAI(
            base_url="https://api.deepinfra.com/v1/openai",
            api_key=API_KEY
        )
        model = 'Qwen/Qwen2.5-72B-Instruct'
    elif llm_selection == "Qwen-QWQ-32B-128k (reasoning)":
        client = OpenAI(
            base_url="https://api.deepinfra.com/v1/openai",
            api_key="06asX0udlOKNwCO7OLYodSViK60k42bF",
        )
        model = 'Qwen/QwQ-32B'
    return client, model

def token_count(content) -> int:
    """Prints a comparison of three string encodings."""
    encoding = tiktoken.get_encoding("o200k_base")
    token_integers = encoding.encode(content)
    num_tokens = len(token_integers)
    return num_tokens

class Workflow:
    def __init__(self, agents):
        self.agents = agents

    async def run(self, input_data) -> AsyncGenerator[dict, None]:
        """Yields agent name, response, and keeps track of total tokens"""
        current_data = input_data
        total_tokens = 0

        for agent in self.agents:
            agent.perceive(input_data)

            async for response in agent.act():  # ✅ Iterate over streamed chunks
                yield response  # ✅ Stream chunks asynchronously

async def async_stream_iterator(sync_stream):
    """Convert a synchronous generator into an async generator."""
    loop = asyncio.get_running_loop()
    for chunk in sync_stream:
        yield await loop.run_in_executor(None, lambda: chunk)

async def validate_chat_and_user(websocket: WebSocket, session: Session, chat_id: int, user_id: int) -> Optional[Dict]:
    """Validate if chat and user exist. Returns dict with chat and user if valid."""
    chat = session.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        await websocket.close(code=1008)  # Policy Violation
        return None

    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        await websocket.close(code=1008)  # Policy Violation
        return None

    return {"chat": chat, "user": user}


async def get_message_history(session: Session, chat_id: int) -> List[Dict]:
    """Retrieve the last five messages in chronological order."""
    last_messages = (
        session.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at.desc())
        .limit(5)
        .all()
    )
    last_messages.reverse()
    return [{"role": msg.role, "content": msg.content} for msg in last_messages]


def deduct_reward(user: User, cost: int = 1) -> bool:
    """Deduct reward from a user. Return False if insufficient rewards."""
    if user.tier != TierEnum.PLATINUM and user.reward < cost:
        return False
    if user.tier != TierEnum.PLATINUM:
        user.reward -= cost
    return True


async def handle_llm_chat(
    websocket: WebSocket,
    session: Session,
    chat_id: int,
    user: User,
    message_history: List[Dict],
    user_message: str,
    regenerate: Optional[bool],
    model_type: str,
    tool_name: str  # Allow None or bool
):
    """Handle LLM chat logic including streaming response and saving messages."""
    # Deduct reward before processing LLM request
    if not deduct_reward(user):
        await websocket.send_text("❌ Not enough rewards to continue chat.")
        await websocket.close(code=1008)
        return

    session.commit()  # Save updated rewards in DB
    if tool_name not in map_tools_name:
        await websocket.send_text("❌ Invalid tool name.")
        await websocket.close(code=1008)
        return
    else:
        # If regenerate, remove the last assistant message from history & database
        if regenerate:
            last_assistant_message = (
                session.query(Message)
                .filter(Message.chat_id == chat_id, Message.role == "assistant")
                .order_by(Message.id.desc())  # Get latest assistant message
                .first()
            )
            if last_assistant_message:
                session.delete(last_assistant_message)
                session.commit()
                # Also remove it from message history
                if message_history and message_history[-1]["role"] == "assistant":
                    message_history.pop()

        # Save user's message if it's not a regeneration request
        if not regenerate:
            user_tokens = token_count(user_message)
            user_message_obj = Message(chat_id=chat_id, role="user", content=user_message, tokens=user_tokens)
            session.add(user_message_obj)
            session.commit()
            print(map_tools_name[tool_name])
            # Add user message to history
            message_history.append({"role":"system", "content": map_tools_name[tool_name]})
            message_history.append(
                {"role": "user", "content": user_message}
                )
            update_chat_title(session, chat_id)
        if model_type == "default":
        # Initialize client and model
            client, model = initialize_client_and_model("Qwen2.5-72B-Instruct-32K")
        elif model_type == "reasonning":
            client, model = initialize_client_and_model("Qwen-QWQ-32B-128k (reasoning)")
        assistant_response = ""
        stream = client.chat.completions.create(
            model=model,
            messages=message_history,
            stream=True,
        )

        async for chunk in async_stream_iterator(stream):
            if websocket.client_state != WebSocketState.CONNECTED:
                print("Client disconnected, stopping stream.")
                break  # Stop processing if client disconnects

            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                assistant_response += content
                await connection_manager.send_message(chat_id, content)

        # Save assistant's response even if client disconnects mid-stream
        if assistant_response.strip():
            assistant_tokens = token_count(assistant_response)

            if regenerate and last_assistant_message:
                # Update last assistant message
                last_assistant_message.content = assistant_response
                last_assistant_message.tokens = assistant_tokens
            else:
                # Create a new assistant message
                assistant_message_obj = Message(
                    chat_id=chat_id, role="assistant", content=assistant_response, tokens=assistant_tokens
                )
                session.add(assistant_message_obj)

            session.commit()

        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close(code=1000)


async def handle_ingredients_checker(
    websocket: WebSocket,
    session: Session,
    chat_id: int,
    user_message: str,
):
    """Handle the ingredients-checker chat logic."""
    # Save user's message
    user_tokens = token_count(user_message)
    user_message_obj = Message(chat_id=chat_id, role="user", content=user_message, tokens=user_tokens)
    session.add(user_message_obj)
    session.commit()

    analysis_workflow = Workflow(get_good_workflow(user_message))
    assistant_response = ""

    async for agent_response in analysis_workflow.run(user_message):
        if websocket.client_state != WebSocketState.CONNECTED:
            print("Client disconnected, stopping stream.")
            break  # Stop processing if client disconnects
        # If the client disconnects, stop the loop
        if chat_id not in connection_manager.active_connections:
            break

        assistant_response += agent_response
        print(agent_response)
        await connection_manager.send_message(chat_id, agent_response)

    # Save assistant's response even if interrupted
    if assistant_response.strip():
        assistant_tokens = token_count(assistant_response)
        assistant_message_obj = Message(
            chat_id=chat_id, role="assistant", content=assistant_response, tokens=assistant_tokens
        )
        session.add(assistant_message_obj)
        session.commit()

    if websocket.client_state == WebSocketState.CONNECTED:
        await websocket.close(code=1000)

def update_chat_title(db: Session, chat_id: int):
    """
    Updates the chat title using the first user message if not already set.
    """
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat or chat.title:
        return  # No chat found or title already set

    first_message = (
        db.query(Message)
        .filter(Message.chat_id == chat_id, Message.role == "user")
        .order_by(Message.created_at.asc())
        .first()
    )

    if first_message and first_message.content:
        chat.title = first_message.content[:50]  # Set title to first message (limit 50 chars)
        db.commit()

