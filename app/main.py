from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
from fastapi.responses import HTMLResponse
from pathlib import Path


app = FastAPI()

HTML_FILE = Path(__file__).parent.parent.parent / "index.html"

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    try:
        return HTML_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "<html><body><h1>Błąd</h1><p>Nie znaleziono pliku index.html.</p></body></html>"


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    await manager.broadcast(f"System: Użytkownik {client_id} połączył się.")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} disconnected")

