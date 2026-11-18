from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..db.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)

    services = relationship("Service", back_populates="categorie", cascade="all, delete-orphan")
