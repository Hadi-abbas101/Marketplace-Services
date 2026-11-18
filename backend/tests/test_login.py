import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app
from app.core.security import get_password_hash

# SQLite en mémoire pour tester l'authentification
SQLITE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Déplacé dans la fixture ci-dessous pour éviter les conflits d'import-time
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Appliquer l'override pour ce module de test
    app.dependency_overrides[get_db] = override_get_db
    
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Créer un utilisateur de test
    db = TestingSessionLocal()
    from app.models import User
    from datetime import date
    test_user = User(
        nom="Martin",
        prenom="Julie",
        courriel="julie.martin@example.com",
        date_naissance=date(1995, 10, 10),
        mot_de_passe_hash=get_password_hash("securepwd123"),
        statut=1
    )
    db.add(test_user)
    db.commit()
    db.close()
    yield
    # Retirer l'override après le test
    app.dependency_overrides.pop(get_db, None)

def test_login_success():
    """Vérifie que la connexion réussit avec des identifiants valides et retourne un jeton JWT."""
    payload = {
        "courriel": "julie.martin@example.com",
        "mot_de_passe": "securepwd123"
    }
    response = client.post("/api/users/login", json=payload)
    assert response.status_code == 200, f"Erreur de connexion : {response.json()}"
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["courriel"] == "julie.martin@example.com"
    assert data["user"]["nom"] == "Martin"
    assert data["user"]["prenom"] == "Julie"

def test_login_invalid_email():
    """Vérifie qu'un email inexistant renvoie une erreur 401."""
    payload = {
        "courriel": "inconnu@example.com",
        "mot_de_passe": "securepwd123"
    }
    response = client.post("/api/users/login", json=payload)
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"]

def test_login_invalid_password():
    """Vérifie qu'un mauvais mot de passe renvoie une erreur 401."""
    payload = {
        "courriel": "julie.martin@example.com",
        "mot_de_passe": "mauvaismdp"
    }
    response = client.post("/api/users/login", json=payload)
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"]
