import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from ..db.database import Base


class Favori(Base):
    __tablename__ = "favoris"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    id_utilisateur = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
    )

    id_service = Column(
        String(36),
        ForeignKey("services.id"),
        nullable=False,
    )

    date_creation = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    utilisateur = relationship(
        "User",
        back_populates="favoris",
    )

    service = relationship(
        "Service",
        back_populates="favoris",
    )

    __table_args__ = (
        UniqueConstraint(
            "id_utilisateur",
            "id_service",
            name="uq_favori_utilisateur_service",
        ),
    )
