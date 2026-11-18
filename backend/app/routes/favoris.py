from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.security import get_current_user
from ..db.database import get_db
from ..models import Favori, Service
from ..schemas import FavoriResponse, FavoriServiceResponse

router = APIRouter(tags=["Favoris"])


@router.post(
    "/api/services/{service_id}/favoris",
    response_model=FavoriResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un service aux favoris",
)
def ajouter_favori(
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

    favori_existant = (
        db.query(Favori)
        .filter(
            Favori.id_utilisateur == current_user["id"],
            Favori.id_service == service_id,
        )
        .first()
    )

    if favori_existant:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce service est déjà dans vos favoris.",
        )

    favori = Favori(
        id_utilisateur=current_user["id"],
        id_service=service_id,
    )

    db.add(favori)
    db.commit()
    db.refresh(favori)

    return favori


@router.delete(
    "/api/services/{service_id}/favoris",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Retirer un service des favoris",
)
def retirer_favori(
    service_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    favori = (
        db.query(Favori)
        .filter(
            Favori.id_utilisateur == current_user["id"],
            Favori.id_service == service_id,
        )
        .first()
    )

    if not favori:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ce service n'est pas dans vos favoris.",
        )

    db.delete(favori)
    db.commit()

    return None


@router.get(
    "/api/favoris",
    response_model=list[FavoriServiceResponse],
    status_code=status.HTTP_200_OK,
    summary="Lister les services favoris de l'utilisateur connecté",
)
def get_mes_favoris(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    favoris = (
        db.query(Favori)
        .filter(Favori.id_utilisateur == current_user["id"])
        .order_by(Favori.date_creation.desc())
        .all()
    )

    return [
        {
            "id": favori.id,
            "id_service": favori.id_service,
            "titre": favori.service.titre,
            "description": favori.service.description,
            "budget_estime": float(favori.service.budget_estime),
            "lieu": favori.service.lieu,
            "categorie_nom": favori.service.categorie.nom,
            "statut": favori.service.statut,
            "date_ajout": favori.date_creation,
        }
        for favori in favoris
    ]
