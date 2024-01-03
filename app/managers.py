from typing import List

from fastapi import WebSocket, WebSocketDisconnect


class WebSocketConnectionManager:
    """
    Manages WebSocket connections for a chat room.

    Attributes:
        active_connections (List[WebSocket]): A list of active WebSocket connections.

    Methods:
        connect(websocket: WebSocket, room_id: str, user_id: str) -> None:
            Connects a WebSocket to the chat room.

        disconnect(websocket: WebSocket, room_id: str) -> None:
            Disconnects a WebSocket from the chat room.

        send_personal_message(message: str, websocket: WebSocket) -> None:
            Sends a personal message to a WebSocket.

        broadcast_message(message: str, room_id: str) -> None:
            Broadcasts a message to all WebSockets in a chat room.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        await websocket.accept()
        self.active_connections.append(
            {"websocket": websocket, "room_id": room_id, "user_id": user_id}
        )

    def disconnect(self, websocket: WebSocket, room_id: str):
        self.active_connections = [
            conn
            for conn in self.active_connections
            if not (conn["websocket"] == websocket and conn["room_id"] == room_id)
        ]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_message(self, message: str, room_id: str):
        for connection in self.active_connections:
            if connection["room_id"] == room_id:
                await connection["websocket"].send_text(message)
