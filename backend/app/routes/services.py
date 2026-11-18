from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..models import Service, User, Category
from ..schemas import ServiceCreate, ServiceDetailResponse, ServiceResponse, ServiceStatutUpdate, CategoryResponse
from ..core.security import get_current_user
from ..services.service_search import query_active_services

router = APIRouter(prefix="/api", tags=["Services"])

BANNED_WORDS = {"drogue", "arme", "violence", "haine", "scam", "fraude", "hack", "piratage", "illégal"}


def check_content_moderation(text: str) -> bool:
    if not text:
        return False
    normalized_text = text.lower()
    for word in BANNED_WORDS:
        if word in normalized_text:
            return True
    return False


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Récupérer la liste des catégories de services",
)
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.get(
    "/services",
    response_model=list[ServiceResponse],
    status_code=status.HTTP_200_OK,
    summary="Récupérer tous les services",
)
def get_services(
    db: Session = Depends(get_db),
    mot_cle: str | None = Query(default=None, max_length=100),
    id_categorie: int | None = Query(default=None),
    budget_max: float | None = Query(default=None, ge=0),
):
    uses_active_query = (
        mot_cle is not None or id_categorie is not None or budget_max is not None
    )
    if not uses_active_query:
        return db.query(Service).filter(Service.statut == "actif").all()

    if id_categorie is not None:
        category = db.query(Category).filter(Category.id == id_categorie).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La catégorie spécifiée n'existe pas.",
            )

    return query_active_services(
        db,
        mot_cle=mot_cle,
        id_categorie=id_categorie,
        budget_max=budget_max,
    )


@router.post(
    "/services",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Publier une offre de service",
)
def create_service(
    service_in: ServiceCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Vérifier si la catégorie existe
    category = db.query(Category).filter(Category.id == service_in.id_categorie).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La catégorie spécifiée n'existe pas.",
        )

    # 2. Modération du contenu
    if check_content_moderation(service_in.titre) or check_content_moderation(service_in.description):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contenu refusé",
        )

    # 3. Créer l'offre de service
    new_service = Service(
        id_utilisateur=current_user["id"],
        id_categorie=service_in.id_categorie,
        titre=service_in.titre,
        description=service_in.description,
        budget_estime=service_in.budget_estime,
        lieu=service_in.lieu,
        photo=service_in.photo,
        statut="actif",
    )

    db.add(new_service)
    db.commit()
    db.refresh(new_service)

    return new_service


@router.get(
    "/services/{service_id}",
    response_model=ServiceDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Récupérer les détails d'un service par son identifiant unique",
)
def get_service_by_id(service_id: str, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Le service spécifié n'existe pas.",
        )

    return {
        "id": service.id,
        "id_utilisateur": service.id_utilisateur,
        "utilisateur_nom": service.utilisateur.nom,
        "utilisateur_prenom": service.utilisateur.prenom,
        "id_categorie": service.id_categorie,
        "categorie_nom": service.categorie.nom,
        "titre": service.titre,
        "description": service.description,
        "budget_estime": float(service.budget_estime),
        "lieu": service.lieu,
        "photo": service.photo,
        "date_creation": service.date_creation,
        "statut": service.statut,
        "note_moyenne": service.note_moyenne,
        "nombre_avis": service.nombre_avis,
    }


@router.put(
    "/services/{service_id}",
    response_model=ServiceDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Modifier un service",
)
def update_service(
    service_id: str,
    payload: ServiceCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = db.query(Service).filter(Service.id == service_id).first()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Le service spécifié n'existe pas.",
        )

    # Optionnel: vérifier que le service appartient à l'utilisateur actuel
    if service.id_utilisateur != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à modifier ce service.",
        )

    categorie = (
        db.query(Category)
        .filter(Category.id == payload.id_categorie)
        .first()
    )

    if not categorie:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La catégorie spécifiée n'existe pas.",
        )

    service.id_categorie = payload.id_categorie
    service.titre = payload.titre
    service.description = payload.description
    service.budget_estime = payload.budget_estime
    service.lieu = payload.lieu
    service.photo = payload.photo

    db.commit()
    db.refresh(service)

    return {
        "id": service.id,
        "id_utilisateur": service.id_utilisateur,
        "utilisateur_nom": service.utilisateur.nom,
        "utilisateur_prenom": service.utilisateur.prenom,
        "id_categorie": service.id_categorie,
        "categorie_nom": service.categorie.nom,
        "titre": service.titre,
        "description": service.description,
        "budget_estime": float(service.budget_estime),
        "lieu": service.lieu,
        "photo": service.photo,
        "date_creation": service.date_creation,
        "statut": service.statut,
        "note_moyenne": service.note_moyenne,
        "nombre_avis": service.nombre_avis,
    }


@router.patch(
    "/services/{service_id}/statut",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Mettre en pause ou réactiver un service",
)
def update_service_statut(
    service_id: str,
    payload: ServiceStatutUpdate,
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
            detail="Vous n'êtes pas autorisé à modifier ce service.",
        )

    if service.statut == "complet":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un service complété ne peut plus être modifié.",
        )

    service.statut = payload.statut

    db.commit()
    db.refresh(service)

    return service


@router.delete(
    "/services/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un service",
)
def delete_service(
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

    # Optionnel: vérifier que le service appartient à l'utilisateur actuel
    if service.id_utilisateur != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à supprimer ce service.",
        )

    db.delete(service)
    db.commit()

    return None
