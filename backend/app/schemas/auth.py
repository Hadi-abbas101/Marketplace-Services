from pydantic import BaseModel, EmailStr, Field

from .user import UserResponse


class UserLogin(BaseModel):
    courriel: EmailStr = Field(..., description="Adresse courriel de l'utilisateur")
    mot_de_passe: str = Field(..., description="Mot de passe de l'utilisateur")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
