from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AvisCreate(BaseModel):
    note: int = Field(..., ge=1, le=5, description="Note de 1 à 5 étoiles")
    commentaire: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Commentaire sur le service",
    )


class AvisResponse(BaseModel):
    id: str
    id_service: str
    id_utilisateur: str
    auteur_nom: str
    auteur_prenom: str
    note: int
    commentaire: str
    date_creation: datetime

    model_config = ConfigDict(from_attributes=True)
