import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from ..db.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    id_service = Column(
        String(36),
        ForeignKey("services.id"),
        nullable=False,
    )

    id_utilisateur_1 = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
    )

    id_utilisateur_2 = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
    )

    date_creation = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    service = relationship("Service", back_populates="conversations")
    utilisateur_1 = relationship("User", foreign_keys=[id_utilisateur_1])
    utilisateur_2 = relationship("User", foreign_keys=[id_utilisateur_2])

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.date_envoi",
    )

    __table_args__ = (
        UniqueConstraint(
            "id_service",
            "id_utilisateur_1",
            "id_utilisateur_2",
            name="uq_conversation_service_users",
        ),
    )
