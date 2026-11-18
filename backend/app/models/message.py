import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship

from ..db.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    id_conversation = Column(
        String(36),
        ForeignKey("conversations.id"),
        nullable=False,
    )

    id_expediteur = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
    )

    contenu = Column(Text, nullable=False)

    date_envoi = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    conversation = relationship("Conversation", back_populates="messages")
    expediteur = relationship("User")
