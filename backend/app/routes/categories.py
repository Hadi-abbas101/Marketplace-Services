from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..models import Category
from ..schemas import CategoryResponse

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get(
    "/",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Récupérer toutes les catégories de services",
)
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()