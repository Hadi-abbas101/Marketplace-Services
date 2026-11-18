from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import User
from ..schemas import UserCreate, UserUpdate
from ..core.security import get_password_hash


def create_user(db: Session, user_in: UserCreate) -> User:
    existing_user = db.query(User).filter(User.courriel == user_in.courriel).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette adresse courriel est déjà associée à un compte existant.",
        )

    user = User(
        nom=user_in.nom,
        prenom=user_in.prenom,
        courriel=user_in.courriel,
        date_naissance=user_in.date_naissance,
        mot_de_passe_hash=get_password_hash(user_in.mot_de_passe),
        statut=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    updates = user_in.model_dump(exclude_unset=True)

    if "courriel" in updates and updates["courriel"] != user.courriel:
        existing_user = db.query(User).filter(User.courriel == updates["courriel"]).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cette adresse courriel est déjà associée à un compte existant.",
            )

    for field, value in updates.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user
