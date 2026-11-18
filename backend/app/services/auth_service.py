from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import User
from ..core.security import create_access_token, verify_password
from ..schemas import UserLogin


INVALID_CREDENTIALS = "Adresse courriel ou mot de passe incorrect."


def authenticate_user(db: Session, credentials: UserLogin) -> dict:
    user = db.query(User).filter(User.courriel == credentials.courriel).first()
    if not user or not verify_password(credentials.mot_de_passe, user.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS,
        )

    return {
        "access_token": create_access_token(data={"sub": user.courriel, "id": user.id}),
        "token_type": "bearer",
        "user": user,
    }
