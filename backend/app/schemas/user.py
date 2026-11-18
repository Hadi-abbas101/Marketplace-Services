from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class UserBase(BaseModel):
    nom: str = Field(..., min_length=1, max_length=50, description="Nom de l'utilisateur")
    prenom: str = Field(..., min_length=1, max_length=50, description="Prénom de l'utilisateur")
    courriel: EmailStr = Field(..., max_length=255, description="Adresse courriel unique")
    date_naissance: date = Field(..., description="Date de naissance au format AAAA-MM-JJ")


class UserCreate(UserBase):
    mot_de_passe: str = Field(..., min_length=8, description="Mot de passe en clair")
    mot_de_passe_confirmation: str = Field(..., min_length=8, description="Confirmation du mot de passe")

    @field_validator("mot_de_passe", "mot_de_passe_confirmation")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Le mot de passe ne doit pas dépasser 72 octets UTF-8")
        return value

    @field_validator("date_naissance")
    @classmethod
    def validate_age(cls, value: date) -> date:
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise ValueError("L'utilisateur doit être majeur (18 ans ou plus)")
        return value

    @model_validator(mode="after")
    def verify_passwords(self) -> "UserCreate":
        if self.mot_de_passe != self.mot_de_passe_confirmation:
            raise ValueError("Le mot de passe et sa confirmation ne correspondent pas")
        return self


class UserUpdate(BaseModel):
    nom: str | None = Field(None, min_length=1, max_length=50, description="Nom de l'utilisateur")
    prenom: str | None = Field(None, min_length=1, max_length=50, description="Prénom de l'utilisateur")
    courriel: EmailStr | None = Field(None, max_length=255, description="Adresse courriel unique")
    date_naissance: date | None = Field(None, description="Date de naissance au format AAAA-MM-JJ")

    @field_validator("date_naissance")
    @classmethod
    def validate_age(cls, value: date | None) -> date | None:
        if value is None:
            return value
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise ValueError("L'utilisateur doit être majeur (18 ans ou plus)")
        return value


class UserResponse(UserBase):
    id: str
    date_creation: datetime
    statut: int

    model_config = ConfigDict(from_attributes=True)


from .service import ServiceResponse


class UserProfileResponse(UserResponse):
    services: list[ServiceResponse] = []

