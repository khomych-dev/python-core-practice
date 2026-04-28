from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, username: str) -> None:
        await websocket.accept()
        if username not in self.active_connections:
            self.active_connections[username] = []
        self.active_connections[username].append(websocket)

    def disconnect(self, websocket: WebSocket, username: str) -> None:
        if username in self.active_connections:
            self.active_connections[username].remove(websocket)
            if not self.active_connections[username]:
                del self.active_connections[username]

    async def send_personal_message(self, message: str, username: str) -> None:
        if username in self.active_connections:
            for connection in self.active_connections[username]:
                await connection.send_text(message)

    async def broadcast(self, message: str) -> None:
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                await connection.send_text(message)


manager = ConnectionManager()
