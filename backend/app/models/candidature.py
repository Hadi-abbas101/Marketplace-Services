import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship

from ..db.database import Base


class Candidature(Base):
    __tablename__ = "candidatures"

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

    id_candidat = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
    )

    message = Column(Text, nullable=False)

    statut = Column(
        String(20),
        default="en_attente",
        nullable=False,
    )

    date_creation = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    service = relationship(
        "Service",
        back_populates="candidatures",
    )

    candidat = relationship(
        "User",
        back_populates="candidatures",
    )

    __table_args__ = (
        UniqueConstraint(
            "id_service",
            "id_candidat",
            name="uq_candidature_service_candidat",
        ),
    )