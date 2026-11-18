from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..models import Conversation, Message, Service
from ..schemas import (
    ConversationDetailResponse,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from ..core.security import decode_token, get_current_user

router = APIRouter(prefix="/api", tags=["Messagerie"])


class ConversationSockets:
    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, conversation_id: str, websocket: WebSocket):
        await websocket.accept()
        if conversation_id not in self._connections:
            self._connections[conversation_id] = []
        self._connections[conversation_id].append(websocket)

    def disconnect(self, conversation_id: str, websocket: WebSocket):
        sockets = self._connections.get(conversation_id, [])
        if websocket in sockets:
            sockets.remove(websocket)
        if not sockets:
            self._connections.pop(conversation_id, None)

    async def broadcast(self, conversation_id: str, message: MessageResponse):
        for websocket in self._connections.get(conversation_id, []):
            await websocket.send_json(message.model_dump(mode="json"))


sockets = ConversationSockets()


def get_or_create_conversation(db: Session, service: Service, user_a_id: str, user_b_id: str) -> Conversation:
    id_utilisateur_1, id_utilisateur_2 = sorted([user_a_id, user_b_id])

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id_service == service.id,
            Conversation.id_utilisateur_1 == id_utilisateur_1,
            Conversation.id_utilisateur_2 == id_utilisateur_2,
        )
        .first()
    )

    if not conversation:
        conversation = Conversation(
            id_service=service.id,
            id_utilisateur_1=id_utilisateur_1,
            id_utilisateur_2=id_utilisateur_2,
        )
        db.add(conversation)
        db.flush()

    return conversation


async def create_message(db: Session, conversation: Conversation, sender_id: str, contenu: str) -> MessageResponse:
    message = Message(id_conversation=conversation.id, id_expediteur=sender_id, contenu=contenu)
    db.add(message)
    db.commit()
    db.refresh(message)

    response = MessageResponse.model_validate(message)
    await sockets.broadcast(conversation.id, response)
    return response


def serialize_conversation(conversation: Conversation, current_user_id: str) -> dict:
    if conversation.id_utilisateur_1 == current_user_id:
        autre = conversation.utilisateur_2
    else:
        autre = conversation.utilisateur_1

    if conversation.messages:
        dernier = conversation.messages[-1]
    else:
        dernier = None

    if dernier:
        dernier_message = dernier.contenu
        date_dernier_message = dernier.date_envoi
    else:
        dernier_message = None
        date_dernier_message = None

    return {
        "id": conversation.id,
        "id_service": conversation.id_service,
        "service_titre": conversation.service.titre,
        "id_autre_utilisateur": autre.id,
        "autre_utilisateur_nom": autre.nom,
        "autre_utilisateur_prenom": autre.prenom,
        "dernier_message": dernier_message,
        "date_dernier_message": date_dernier_message,
    }


def serialize_conversation_detail(conversation: Conversation, current_user_id: str) -> dict:
    result = serialize_conversation(conversation, current_user_id)
    result["messages"] = conversation.messages
    return result


def get_date_dernier_message(conversation: dict):
    return conversation["date_dernier_message"]


def is_participant(conversation: Conversation, user_id: str) -> bool:
    return user_id in (conversation.id_utilisateur_1, conversation.id_utilisateur_2)


def get_conversation_or_404(db: Session, conversation_id: str, current_user_id: str) -> Conversation:
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation introuvable.")
    if not is_participant(conversation, current_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas accès à cette conversation.")
    return conversation


@router.post(
    "/services/{service_id}/messages",
    response_model=ConversationDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Envoyer un message au propriétaire d'un service",
)
async def send_service_message(
    service_id: str,
    payload: MessageCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Le service spécifié n'existe pas.")
    if service.id_utilisateur == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas vous envoyer un message à vous-même.",
        )

    conversation = get_or_create_conversation(db, service, current_user["id"], service.id_utilisateur)
    await create_message(db, conversation, current_user["id"], payload.contenu)

    return serialize_conversation_detail(conversation, current_user["id"])


@router.get(
    "/conversations",
    response_model=list[ConversationResponse],
    summary="Récupérer les conversations de l'utilisateur connecté",
)
def get_conversations(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    conversations = (
        db.query(Conversation)
        .filter(
            or_(
                Conversation.id_utilisateur_1 == current_user["id"],
                Conversation.id_utilisateur_2 == current_user["id"],
            )
        )
        .all()
    )

    serialized = []
    for conversation in conversations:
        serialized.append(serialize_conversation(conversation, current_user["id"]))

    serialized.sort(key=get_date_dernier_message, reverse=True)
    return serialized


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
    summary="Récupérer une conversation et ses messages",
)
def get_conversation(conversation_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = get_conversation_or_404(db, conversation_id, current_user["id"])
    return serialize_conversation_detail(conversation, current_user["id"])


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Envoyer un message dans une conversation existante",
)
async def send_message(
    conversation_id: str,
    payload: MessageCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = get_conversation_or_404(db, conversation_id, current_user["id"])
    return await create_message(db, conversation, current_user["id"], payload.contenu)


@router.websocket("/ws/conversations/{conversation_id}")
async def conversation_websocket(
    websocket: WebSocket,
    conversation_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    user = decode_token(token)
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not user or not conversation or not is_participant(conversation, user["id"]):
        await websocket.close(code=4403)
        return

    await sockets.connect(conversation_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        sockets.disconnect(conversation_id, websocket)
