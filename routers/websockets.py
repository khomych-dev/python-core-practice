from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.ws_manager import ws_manager

router = APIRouter(tags=["Real-time"])


@router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.broadcast(f"Client says: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
