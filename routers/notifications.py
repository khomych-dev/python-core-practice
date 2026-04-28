import jwt
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from security import ALGORITHM, SECRET_KEY
from services.notification_service import manager

router = APIRouter(prefix="/ws", tags=["Notifications"])


@router.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)) -> None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")

        if not username:
            await websocket.close(code=1008, reason="Invalid token payload")
            return

    except jwt.ExpiredSignatureError:
        await websocket.close(code=1008, reason="Token expired")
        return
    except jwt.InvalidTokenError:
        await websocket.close(code=1008, reason="Invalid token")
        return

    await manager.connect(websocket, username)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, username)
