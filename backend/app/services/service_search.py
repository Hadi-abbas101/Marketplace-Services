from decimal import Decimal

from sqlalchemy.orm import Session

from ..models import Service
from ..utils.text_normalize import normalize_text

ACTIVE_STATUS = "actif"


def query_active_services(
    db: Session,
    mot_cle: str | None = None,
    id_categorie: int | None = None,
    budget_max: float | None = None,
) -> list[Service]:
    """Retourne les services actifs filtrés par mot-clé, catégorie et budget maximum."""
    query = db.query(Service).filter(Service.statut == ACTIVE_STATUS)

    if id_categorie is not None:
        query = query.filter(Service.id_categorie == id_categorie)

    if budget_max is not None:
        query = query.filter(Service.budget_estime <= Decimal(str(budget_max)))

    services = query.all()

    if mot_cle is not None:
        term = mot_cle.strip()
        if term:
            normalized_term = normalize_text(term)
            services = [
                service
                for service in services
                if normalized_term in normalize_text(service.titre)
                or normalized_term in normalize_text(service.description)
            ]

    return services


def search_active_services(db: Session, mot_cle: str | None) -> list[Service]:
    return query_active_services(db, mot_cle=mot_cle)
