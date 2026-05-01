import jwt
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from security import ALGORITHM, SECRET_KEY
from services.ws_manager import ws_manager

router = APIRouter(tags=["Real-time"])


@router.websocket("/ws/notifications")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str | None = Query(None),
) -> None:
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")

        if not username:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        print(f"WebSocket Auth Error: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await ws_manager.connect(websocket)
    try:
        while True:
            _ = await websocket.receive_text()

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
