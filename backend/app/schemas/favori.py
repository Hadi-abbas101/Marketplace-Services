from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FavoriResponse(BaseModel):
    id: str
    id_utilisateur: str
    id_service: str
    date_creation: datetime

    model_config = ConfigDict(from_attributes=True)


class FavoriServiceResponse(BaseModel):
    """Favori enrichi des informations du service, pour l'affichage dans le tableau de bord."""

    id: str
    id_service: str
    titre: str
    description: str
    budget_estime: float
    lieu: str
    categorie_nom: str
    statut: str
    date_ajout: datetime

    model_config = ConfigDict(from_attributes=True)
