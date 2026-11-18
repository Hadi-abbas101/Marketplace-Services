from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.security import get_current_user
from ..db.database import get_db
from ..models import Avis, Service
from ..schemas import AvisCreate, AvisResponse

router = APIRouter(tags=["Avis"])


@router.post(
    "/api/services/{service_id}/avis",
    response_model=AvisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Laisser un avis sur un service",
)
def creer_avis(
    service_id: str,
    payload: AvisCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = db.query(Service).filter(Service.id == service_id).first()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Le service spécifié n'existe pas.",
        )

    if service.id_utilisateur == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas laisser un avis sur votre propre service.",
        )

    avis_existant = (
        db.query(Avis)
        .filter(
            Avis.id_utilisateur == current_user["id"],
            Avis.id_service == service_id,
        )
        .first()
    )

    if avis_existant:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vous avez déjà laissé un avis sur ce service.",
        )

    avis = Avis(
        id_service=service_id,
        id_utilisateur=current_user["id"],
        note=payload.note,
        commentaire=payload.commentaire,
    )

    db.add(avis)
    db.commit()
    db.refresh(avis)

    return avis


@router.get(
    "/api/services/{service_id}/avis",
    response_model=list[AvisResponse],
    status_code=status.HTTP_200_OK,
    summary="Lister les avis d'un service",
)
def get_avis_service(service_id: str, db: Session = Depends(get_db)):
    return (
        db.query(Avis)
        .filter(Avis.id_service == service_id)
        .order_by(Avis.date_creation.desc())
        .all()
    )
