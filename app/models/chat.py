from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class ChatMessage(Base):
    """
    Represents a chat message.

    Attributes:
        id (int): The unique identifier of the message.
        user_id (str): The ID of the user who sent the message.
        room_id (str): The ID of the chat room where the message was sent.
        content (str): The content of the message.
        timestamp (datetime): The timestamp when the message was created.
    """

    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    room_id = Column(String, index=True)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


class PrivateMessage(Base):
    """
    Represents a private message between two users.
    """

    __tablename__ = "private_messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String, index=True)
    receiver_id = Column(String, index=True)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
