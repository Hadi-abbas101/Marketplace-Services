from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.security import get_current_user
from ..db.database import get_db
from ..models import Candidature, Service
from ..schemas import (
    CandidatureCreate,
    CandidatureDetailResponse,
    CandidatureMineResponse,
    CandidatureResponse,
    CandidatureStatusUpdate,
)

router = APIRouter(tags=["Candidatures"])


@router.get(
    "/api/candidatures/me",
    response_model=list[CandidatureMineResponse],
    status_code=status.HTTP_200_OK,
    summary="Voir mes candidatures envoyées",
)
def get_mes_candidatures(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidatures = (
        db.query(Candidature)
        .filter(Candidature.id_candidat == current_user["id"])
        .order_by(Candidature.date_creation.desc())
        .all()
    )

    return [
        {
            "id": candidature.id,
            "id_service": candidature.id_service,
            "id_candidat": candidature.id_candidat,
            "service_titre": candidature.service.titre,
            "service_statut": candidature.service.statut,
            "message": candidature.message,
            "statut": candidature.statut,
            "date_creation": candidature.date_creation,
        }
        for candidature in candidatures
    ]


@router.post(
    "/api/services/{service_id}/candidatures",
    response_model=CandidatureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Postuler sur un service",
)
def postuler_sur_service(
    service_id: str,
    payload: CandidatureCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = db.query(Service).filter(Service.id == service_id).first()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Le service spécifié n'existe pas.",
        )

    if service.statut != "actif":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Il n'est pas possible de postuler sur ce service.",
        )

    if service.id_utilisateur == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas postuler sur votre propre service.",
        )

    candidature_existante = (
        db.query(Candidature)
        .filter(
            Candidature.id_service == service_id,
            Candidature.id_candidat == current_user["id"],
        )
        .first()
    )

    if candidature_existante:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vous avez déjà postulé sur ce service.",
        )

    candidature = Candidature(
        id_service=service_id,
        id_candidat=current_user["id"],
        message=payload.message,
    )

    db.add(candidature)
    db.commit()
    db.refresh(candidature)

    return candidature


@router.get(
    "/api/services/{service_id}/candidatures",
    response_model=list[CandidatureDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Voir les candidatures d'un service",
)
def get_candidatures_service(
    service_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = db.query(Service).filter(Service.id == service_id).first()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Le service spécifié n'existe pas.",
        )

    if service.id_utilisateur != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le propriétaire du service peut consulter les candidatures.",
        )

    candidatures = (
        db.query(Candidature)
        .filter(Candidature.id_service == service_id)
        .order_by(Candidature.date_creation.desc())
        .all()
    )

    return [
        {
            "id": candidature.id,
            "id_service": candidature.id_service,
            "id_candidat": candidature.id_candidat,
            "candidat_nom": candidature.candidat.nom,
            "candidat_prenom": candidature.candidat.prenom,
            "candidat_courriel": candidature.candidat.courriel,
            "message": candidature.message,
            "statut": candidature.statut,
            "date_creation": candidature.date_creation,
        }
        for candidature in candidatures
    ]


@router.patch(
    "/api/candidatures/{candidature_id}/statut",
    response_model=CandidatureDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Accepter ou refuser une candidature",
)
def modifier_statut_candidature(
    candidature_id: str,
    payload: CandidatureStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidature = (
        db.query(Candidature)
        .filter(Candidature.id == candidature_id)
        .first()
    )

    if not candidature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La candidature spécifiée n'existe pas.",
        )

    if candidature.service.id_utilisateur != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le propriétaire du service peut traiter cette candidature.",
        )

    if candidature.statut != "en_attente":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette candidature a déjà été traitée.",
        )

    candidature.statut = payload.statut
    if payload.statut == "acceptee":
        candidature.service.statut = "complet"

    db.commit()
    db.refresh(candidature)

    return {
        "id": candidature.id,
        "id_service": candidature.id_service,
        "id_candidat": candidature.id_candidat,
        "candidat_nom": candidature.candidat.nom,
        "candidat_prenom": candidature.candidat.prenom,
        "candidat_courriel": candidature.candidat.courriel,
        "message": candidature.message,
        "statut": candidature.statut,
        "date_creation": candidature.date_creation,
    }