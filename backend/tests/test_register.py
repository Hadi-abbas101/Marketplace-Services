import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app

# Utilisation de SQLite en mémoire avec StaticPool pour conserver les connexions actives
SQLITE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Créer les tables sur la base de données de test en mémoire
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Remplacer la dépendance get_db par celle de test
# Déplacé dans la fixture ci-dessous pour éviter les conflits d'import-time

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    # Appliquer l'override pour ce module de test
    app.dependency_overrides[get_db] = override_get_db
    # Nettoyer et recréer la structure de la base à chaque test pour l'isolation
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Retirer l'override après le test
    app.dependency_overrides.pop(get_db, None)

def test_register_user_success():
    """Vérifie le succès d'une inscription valide d'un utilisateur majeur."""
    payload = {
        "nom": "Dupont",
        "prenom": "Jean",
        "courriel": "jean.dupont@example.com",
        "date_naissance": "2000-01-01",
        "mot_de_passe": "password123",
        "mot_de_passe_confirmation": "password123"
    }
    response = client.post("/api/users/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nom"] == "Dupont"
    assert data["prenom"] == "Jean"
    assert data["courriel"] == "jean.dupont@example.com"
    assert "id" in data
    assert "mot_de_passe_hash" not in data  # Sécurité : le mot de passe ne doit pas être renvoyé

def test_register_user_underage():
    """Vérifie qu'un utilisateur de moins de 18 ans est bloqué par la validation."""
    # Calculer une date de naissance pour une personne de 17 ans
    dob = date.today() - timedelta(days=17 * 365)
    payload = {
        "nom": "Dupont",
        "prenom": "Jean",
        "courriel": "jean.dupont@example.com",
        "date_naissance": dob.isoformat(),
        "mot_de_passe": "password123",
        "mot_de_passe_confirmation": "password123"
    }
    response = client.post("/api/users/register", json=payload)
    assert response.status_code == 422  # Erreur de validation de schéma
    assert "majeur" in response.text

def test_register_user_email_conflict():
    """Vérifie qu'une tentative avec un email déjà existant renvoie une erreur 409."""
    payload1 = {
        "nom": "Dupont",
        "prenom": "Jean",
        "courriel": "dupont@example.com",
        "date_naissance": "2000-01-01",
        "mot_de_passe": "password123",
        "mot_de_passe_confirmation": "password123"
    }
    # Premier appel : Succès
    res1 = client.post("/api/users/register", json=payload1)
    assert res1.status_code == 201

    payload2 = {
        "nom": "Martin",
        "prenom": "Marie",
        "courriel": "dupont@example.com",  # Même courriel
        "date_naissance": "1999-02-02",
        "mot_de_passe": "pass4567",
        "mot_de_passe_confirmation": "pass4567"
    }
    # Deuxième appel : Conflit
    res2 = client.post("/api/users/register", json=payload2)
    assert res2.status_code == 409
    assert "compte existant" in res2.json()["detail"]

def test_register_user_password_mismatch():
    """Vérifie que des mots de passe qui ne correspondent pas sont bloqués."""
    payload = {
        "nom": "Dupont",
        "prenom": "Jean",
        "courriel": "jean.dupont@example.com",
        "date_naissance": "2000-01-01",
        "mot_de_passe": "password123",
        "mot_de_passe_confirmation": "differentpassword"
    }
    response = client.post("/api/users/register", json=payload)
    assert response.status_code == 422
    assert "ne correspondent pas" in response.text


def test_register_rejects_password_over_bcrypt_byte_limit():
    from pydantic import ValidationError
    from app.schemas import UserCreate
    with pytest.raises(ValidationError):
        UserCreate(nom="Test", prenom="Test", courriel="test@example.com",
                   date_naissance="2000-01-01", mot_de_passe="é" * 37,
                   mot_de_passe_confirmation="é" * 37)


def test_login_rejects_password_over_bcrypt_byte_limit():
    from app.core.security import get_password_hash, verify_password
    assert not verify_password("é" * 37, get_password_hash("validPassword123"))
