from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, websocket: WebSocket, client_id: str):
        self.active_connections.pop(client_id, None)

    async def broadcast(self, message: dict, exclude_id: str | None = None):
        for client_id, websocket in self.active_connections.items():
            if client_id != exclude_id:
                await websocket.send_json(message)

    async def send_personal_message(self, message: dict, client_id: str):
        websocket_gracza = self.active_connections.get(client_id)
        if websocket_gracza:
            await websocket_gracza.send_json(message)

manager = ConnectionManager()