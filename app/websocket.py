from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.managers import WebSocketConnectionManager
from app.models.chat import ChatMessage, PrivateMessage

router = APIRouter()
manager = WebSocketConnectionManager()


@router.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Handle WebSocket connections for chat functionality.

    Parameters:
    - websocket (WebSocket): The WebSocket connection.
    - room_id (str): The ID of the chat room.
    - user_id (str): The ID of the user connecting to the WebSocket (obtained from the current user).
    - db (Session): The database session.

    Returns:
    None

    Raises:
    None
    """
    await manager.connect(websocket, room_id, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = ChatMessage(user_id=user_id, room_id=room_id, content=data)

            db.add(message)
            db.commit()

            await manager.broadcast_message(f"{user_id}: {data}", room_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast_message(f"User {user_id} left the room", room_id)


@router.websocket("/ws_private/{other_user_id}")
async def private_message_websocket(
    websocket: WebSocket,
    other_user_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Handle WebSocket connection for private messaging.

    Args:
        websocket (WebSocket): The WebSocket connection.
        other_user_id (str): The ID of the other user in the private chat.
        current_user (str, optional): The ID of the current user. Defaults to Depends(get_current_user).
        db (Session, optional): The database session. Defaults to Depends(get_db).
    """
    await manager.connect_private(websocket, other_user_id, current_user)

    try:
        while True:
            data = await websocket.receive_text()
            message = PrivateMessage(
                sender_id=current_user, receiver_id=other_user_id, content=data
            )

            db.add(message)
            db.commit()

            await manager.broadcast_private_message(
                f"{current_user}: {data}", other_user_id
            )
    except WebSocketDisconnect:
        manager.disconnect_private(websocket, other_user_id)
        await manager.broadcast_private_message(
            f"User {current_user} left the private chat", other_user_id
        )
