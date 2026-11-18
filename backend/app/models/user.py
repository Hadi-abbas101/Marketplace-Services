import uuid

from sqlalchemy import Column, Date, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from ..db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    nom = Column(String(50), nullable=False)
    prenom = Column(String(50), nullable=False)

    courriel = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    date_naissance = Column(Date, nullable=False)
    mot_de_passe_hash = Column(String(255), nullable=False)

    date_creation = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    statut = Column(
        Integer,
        default=1,
        nullable=False,
    )

    services = relationship(
        "Service",
        back_populates="utilisateur",
        cascade="all, delete-orphan",
    )

    candidatures = relationship(
        "Candidature",
        back_populates="candidat",
        cascade="all, delete-orphan",
    )

    favoris = relationship(
        "Favori",
        back_populates="utilisateur",
        cascade="all, delete-orphan",
    )

    avis = relationship(
        "Avis",
        back_populates="auteur",
        cascade="all, delete-orphan",
    )