from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    contenu: str = Field(..., min_length=1, max_length=2000, description="Contenu du message")


class MessageResponse(BaseModel):
    id: str
    id_conversation: str
    id_expediteur: str
    contenu: str
    date_envoi: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    id: str
    id_service: str
    service_titre: str
    id_autre_utilisateur: str
    autre_utilisateur_nom: str
    autre_utilisateur_prenom: str
    dernier_message: str | None = None
    date_dernier_message: datetime | None = None


class ConversationDetailResponse(ConversationResponse):
    messages: list[MessageResponse]
