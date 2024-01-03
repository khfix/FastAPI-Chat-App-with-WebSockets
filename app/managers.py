# app/managers.py

from typing import List

from fastapi import WebSocket, WebSocketDisconnect


class WebSocketConnectionManager:
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
