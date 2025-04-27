from typing import Dict
from fastapi import WebSocket
from starlette.websockets import WebSocketState

class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}  # Store connections by chat_id

    async def connect(self, chat_id: int, websocket: WebSocket):
        """Accept new WebSocket connection and store it."""
        await websocket.accept()
        self.active_connections[chat_id] = websocket

    async def disconnect(self, chat_id: int):
        """Remove connection when the user disconnects."""
        websocket = self.active_connections.pop(chat_id, None)  # Remove safely
        if websocket:
            if websocket.client_state == WebSocketState.CONNECTED:  # ✅ Ensure it's still connected
                try:
                    await websocket.close(code=1000)
                except RuntimeError:
                    print(f"WebSocket {chat_id} was already closed.")

    async def send_message(self, chat_id: int, message: str):
        """Send a message to a specific user/chat_id."""
        websocket = self.active_connections.get(chat_id)
        if websocket and websocket.client_state == WebSocketState.CONNECTED:  # ✅ Ensure it's open
            try:
                await websocket.send_text(message)
            except RuntimeError:
                print(f"Cannot send message to closed WebSocket {chat_id}.")

    async def broadcast(self, message: str):
        """Broadcast a message to all connected clients."""
        for websocket in self.active_connections.values():
            await websocket.send_text(message)

# Create an instance
connection_manager = WebSocketConnectionManager()
