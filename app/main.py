from typing import List
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path
from app.services.connection_manager import manager
from app.routers import game_ws


app = FastAPI()

HTML_FILE = Path(__file__).parent.parent / "index.html"

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    try:
        return HTML_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "<html><body><h1>Błąd</h1><p>Nie znaleziono pliku index.html.</p></body></html>"


app.include_router(game_ws.router)
