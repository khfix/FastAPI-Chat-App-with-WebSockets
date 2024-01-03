# app/chat.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.chat import ChatMessage, PrivateMessage

router = APIRouter()


@router.get("/history/{room_id}")
async def get_chat_history(room_id: str, db: Session = Depends(get_db)):
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
    # Create and store the private message in the database
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
    # Retrieve private messages between the current user and the specified user
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
