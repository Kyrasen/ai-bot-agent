from fastapi import APIRouter, WebSocket
from websocket_handler import handle_ws

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await handle_ws(websocket)


