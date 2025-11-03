from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict
from fastapi.responses import HTMLResponse
from pathlib import Path


app = FastAPI()

HTML_FILE = Path(__file__).parent.parent / "index.html"

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    try:
        return HTML_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "<html><body><h1>Błąd</h1><p>Nie znaleziono pliku index.html.</p></body></html>"


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

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    if client_id in manager.active_connections:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, client_id)
    await manager.send_personal_message({"typ": "system", "wiadomosc": f"Witaj, {client_id}!"}, client_id)
    await manager.broadcast({"typ": "system", "wiadomosc": f"Użytkownik {client_id} dołączył."}, exclude_id=client_id)
        
    try:
        while True:
            data = await websocket.receive_json()
            if data['typ'] == 'czat':
                wiadomosc_do_wyslania = {"nadawca": client_id, "typ": "czat", "wiadomosc": data['wiadomosc']}
                await manager.broadcast(wiadomosc_do_wyslania)
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
        await manager.broadcast({"typ": "system", "wiadomosc": f"Użytkownik {client_id} rozłączył się."})

