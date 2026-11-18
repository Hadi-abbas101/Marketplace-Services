from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..schemas import TokenResponse, UserCreate, UserUpdate, UserLogin, UserResponse, UserProfileResponse
from ..services.auth_service import authenticate_user
from ..services.user_service import create_user, update_user
from ..core.security import get_current_user


router = APIRouter(prefix="/api/users", tags=["Utilisateurs"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription d'un nouvel utilisateur",
)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user_in)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Connexion d'un utilisateur",
)
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    return authenticate_user(db, credentials)


@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Récupérer le profil de l'utilisateur connecté",
)
def get_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from ..models import User
    user = db.query(User).filter(User.id == current_user["id"]).first()
    return user


@router.put(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Modifier le profil de l'utilisateur connecté",
)
def update_user_profile(
    user_in: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from ..models import User
    user = db.query(User).filter(User.id == current_user["id"]).first()
    return update_user(db, user, user_in)

