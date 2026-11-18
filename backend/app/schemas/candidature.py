from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CandidatureCreate(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Message envoyé avec la candidature",
    )


class CandidatureStatusUpdate(BaseModel):
    statut: Literal["acceptee", "refusee"]


class CandidatureResponse(BaseModel):
    id: str
    id_service: str
    id_candidat: str
    message: str
    statut: str
    date_creation: datetime

    model_config = ConfigDict(from_attributes=True)


class CandidatureDetailResponse(CandidatureResponse):
    candidat_nom: str
    candidat_prenom: str
    candidat_courriel: str


class CandidatureMineResponse(CandidatureResponse):
    """Candidature envoyée par l'utilisateur, enrichie du service visé (tableau de bord)."""

    service_titre: str
    service_statut: str