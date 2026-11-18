import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from ..db.database import Base


class Service(Base):
    __tablename__ = "services"

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

    id_categorie = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False,
    )

    titre = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    photo = Column(Text, nullable=True)

    budget_estime = Column(
        Numeric(10, 2),
        default=0.00,
        nullable=False,
    )

    lieu = Column(String(100), nullable=False)

    date_creation = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    statut = Column(
        String(20),
        default="actif",
        nullable=False,
    )

    utilisateur = relationship(
        "User",
        back_populates="services",
    )

    categorie = relationship(
        "Category",
        back_populates="services",
    )

    candidatures = relationship(
        "Candidature",
        back_populates="service",
        cascade="all, delete-orphan",
    )

    favoris = relationship(
        "Favori",
        back_populates="service",
        cascade="all, delete-orphan",
    )

    avis = relationship(
        "Avis",
        back_populates="service",
        cascade="all, delete-orphan",
    )

    conversations = relationship(
        "Conversation",
        back_populates="service",
        cascade="all, delete-orphan",
    )

    @property
    def note_moyenne(self) -> float | None:
        if not self.avis:
            return None
        return round(sum(a.note for a in self.avis) / len(self.avis), 1)

    @property
    def nombre_avis(self) -> int:
        return len(self.avis)