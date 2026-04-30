import asyncio
import json

from fastapi import WebSocket
from redis.asyncio import Redis

from config import settings


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


async def listen_for_notifications() -> None:
    redis = Redis.from_url(settings.redis_url)
    pubsub = redis.pubsub()
    await pubsub.subscribe("notifications")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                target_user = data.get("username")
                text = data.get("message", "A new notification has been received")

                if target_user:
                    await manager.send_personal_message(text, target_user)
                else:
                    await manager.broadcast(text)
    except asyncio.CancelledError:
        await pubsub.unsubscribe("notifications")
    finally:
        await redis.close()
