from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.connection_manager import manager 

router = APIRouter()

@router.websocket("/ws/{client_id}")
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