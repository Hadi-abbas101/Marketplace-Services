import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from ..db.database import Base


class Avis(Base):
    __tablename__ = "avis"

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

    id_utilisateur = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
    )

    note = Column(Integer, nullable=False)
    commentaire = Column(Text, nullable=False)

    date_creation = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    service = relationship(
        "Service",
        back_populates="avis",
    )

    auteur = relationship(
        "User",
        back_populates="avis",
    )

    __table_args__ = (
        UniqueConstraint(
            "id_utilisateur",
            "id_service",
            name="uq_avis_utilisateur_service",
        ),
    )

    @property
    def auteur_nom(self) -> str:
        return self.auteur.nom

    @property
    def auteur_prenom(self) -> str:
        return self.auteur.prenom
