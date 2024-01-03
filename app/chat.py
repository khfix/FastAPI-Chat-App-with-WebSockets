from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.chat import ChatMessage, PrivateMessage

router = APIRouter()


@router.get("/history/{room_id}")
async def get_chat_history(room_id: str, db: Session = Depends(get_db)):
    """
    Retrieve the chat history for a specific room.

    Args:
        room_id (str): The ID of the room.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: A dictionary containing the chat history messages.
            Each message is represented by a dictionary with "user_id" and "content" keys.
    """
    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.room_id == room_id)
        .order_by(ChatMessage.timestamp)
        .all()
    )
    return {
        "messages": [
            {"user_id": msg.user_id, "content": msg.content} for msg in history
        ]
    }


@router.post("/send_private_message")
async def send_private_message(
    receiver_id: str,
    content: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send a private message to a user.

    Args:
        receiver_id (str): The ID of the user who will receive the message.
        content (str): The content of the message.
        current_user (str, optional): The ID of the current user. Defaults to the result of the `get_current_user` dependency.
        db (Session, optional): The database session. Defaults to the result of the `get_db` dependency.

    Returns:
        dict: A dictionary with a success message indicating that the private message was sent successfully.
    """
    message = PrivateMessage(
        sender_id=current_user, receiver_id=receiver_id, content=content
    )
    db.add(message)
    db.commit()
    return {"message": "Private message sent successfully"}


@router.get("/private_messages/{other_user_id}")
async def get_private_messages(
    other_user_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve private messages between the current user and another user.

    Args:
        other_user_id (str): The ID of the other user.
        current_user (str, optional): The ID of the current user. Defaults to the user obtained from the `get_current_user` dependency.
        db (Session, optional): The database session. Defaults to the session obtained from the `get_db` dependency.

    Returns:
        dict: A dictionary containing the retrieved private messages, with each message represented as a dictionary with "sender_id" and "content" keys.
    """
    messages = (
        db.query(PrivateMessage)
        .filter(
            or_(
                and_(
                    PrivateMessage.sender_id == current_user,
                    PrivateMessage.receiver_id == other_user_id,
                ),
                and_(
                    PrivateMessage.sender_id == other_user_id,
                    PrivateMessage.receiver_id == current_user,
                ),
            )
        )
        .order_by(PrivateMessage.timestamp)
        .all()
    )

    return {
        "messages": [
            {"sender_id": msg.sender_id, "content": msg.content} for msg in messages
        ]
    }
