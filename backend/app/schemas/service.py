from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ServiceCreate(BaseModel):
    id_categorie: int = Field(..., description="ID de la catégorie du service")
    titre: str = Field(..., min_length=1, max_length=100, description="Titre descriptif du service")
    description: str = Field(..., min_length=1, max_length=1000, description="Description détaillée du service")
    budget_estime: float = Field(default=0.00, ge=0.0, description="Budget estimé en dollars")
    lieu: str = Field(..., min_length=1, max_length=100, description="Lieu de réalisation (ville, région)")
    photo: str | None = Field(default=None, max_length=7_000_000, description="Photo du service encodée en base64 (data URL)")


class ServiceStatutUpdate(BaseModel):
    statut: Literal["actif", "en_pause"]


class ServiceResponse(BaseModel):
    id: str
    id_utilisateur: str
    id_categorie: int
    titre: str
    description: str
    budget_estime: float
    lieu: str
    photo: str | None = None
    date_creation: datetime
    statut: str
    note_moyenne: float | None = None
    nombre_avis: int = 0

    model_config = ConfigDict(from_attributes=True)


class ServiceDetailResponse(BaseModel):
    id: str
    id_utilisateur: str
    utilisateur_nom: str
    utilisateur_prenom: str
    id_categorie: int
    categorie_nom: str
    titre: str
    description: str
    budget_estime: float
    lieu: str
    photo: str | None = None
    date_creation: datetime
    statut: str
    note_moyenne: float | None = None
    nombre_avis: int = 0

    model_config = ConfigDict(from_attributes=True)
